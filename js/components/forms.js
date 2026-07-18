import { qs, qsa } from '../core/dom.js';
import { loadSharedData } from '../core/data.js';
import { currentPage } from '../core/page.js';
import { APPROVED, state } from '../core/state.js';

export function initForms() {
  qsa('form.sf-form, form[data-enhanced-form], form[data-consultation-form]').forEach((form, formIndex) => {
    if (form.dataset.sfFormReady === 'true') return;
    form.dataset.sfFormReady = 'true';
    form.setAttribute('data-enhanced-form', '');
    form.noValidate = true;
    form.method = 'post';

    const page = currentPage();
    const isConsultation = page === 'consultation' || /consultation|consulta/i.test(qs('button[type="submit"]', form)?.textContent || '');

    const formId = form.id || `sf-form-${formIndex + 1}`;
    if (!form.id) form.id = formId;
    const stateNodes = qsa('[data-form-state]', form);
    const renderedStateCopy = Object.fromEntries(
      stateNodes.map((node) => [node.dataset.formState, node.textContent.trim()])
    );
    const copy = {
      required: form.dataset.messageRequired || '',
      email: form.dataset.messageEmail || '',
      review: form.dataset.messageReview || '',
      loading: renderedStateCopy.loading || '',
      success: renderedStateCopy.success || '',
      error: renderedStateCopy.error || ''
    };
    let status = qs('[data-form-status]', form);
    if (!status && !stateNodes.length) {
      status = document.createElement('p');
      status.dataset.formStatus = '';
      status.className = 'sf-form-status';
      status.id = `${formId}-status`;
      status.hidden = true;
      status.tabIndex = -1;
      form.append(status);
    }
    if (status?.id) {
      form.setAttribute('aria-describedby', [form.getAttribute('aria-describedby'), status.id].filter(Boolean).join(' '));
    }

    const clearFieldError = (field) => {
      const errorId = field.dataset.sfErrorId;
      const error = errorId ? document.getElementById(errorId) : null;
      if (error?.dataset.errorFor) {
        error.textContent = '';
        error.hidden = true;
      } else {
        error?.remove();
        const describedBy = (field.getAttribute('aria-describedby') || '').split(/\s+/).filter((id) => id && id !== errorId);
        if (describedBy.length) field.setAttribute('aria-describedby', describedBy.join(' '));
        else field.removeAttribute('aria-describedby');
      }
      delete field.dataset.sfErrorId;
      field.classList.remove('is-invalid');
      field.removeAttribute('aria-invalid');
    };

    const showFieldError = (field, message) => {
      clearFieldError(field);
      const safeName = String(field.name || field.id || 'field').replace(/[^a-z0-9_-]+/gi, '-');
      let error = qsa('[data-error-for]', form).find((node) => node.dataset.errorFor === field.id);
      if (!error) {
        error = document.createElement('p');
        error.id = `${formId}-${safeName}-runtime-error`;
        error.className = 'form-error';
        field.insertAdjacentElement('afterend', error);
      }
      error.textContent = message;
      error.hidden = false;
      field.dataset.sfErrorId = error.id;
      field.classList.add('is-invalid');
      field.setAttribute('aria-invalid', 'true');
      const describedBy = new Set((field.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean));
      describedBy.add(error.id);
      field.setAttribute('aria-describedby', Array.from(describedBy).join(' '));
    };

    const fields = qsa('input, select, textarea', form).filter((field) => !field.classList.contains('sf-honeypot') && field.type !== 'hidden');
    fields.forEach((field) => {
      const clear = () => clearFieldError(field);
      field.addEventListener('input', clear);
      field.addEventListener('change', clear);
    });

    const validate = () => {
      let firstInvalid = null;
      let errorCount = 0;
      fields.forEach(clearFieldError);
      fields.forEach((field) => {
        if (field.disabled || field.checkValidity()) return;
        errorCount += 1;
        const message = field.validity.typeMismatch ? copy.email : copy.required;
        showFieldError(field, message);
        if (!firstInvalid) firstInvalid = field;
      });
      return { firstInvalid, errorCount };
    };

    // Analytics receives lifecycle states, never FormData or field values.
    // A successful event is emitted only after Formspree confirms the request.
    const emitLifecycle = (name, detail = {}) => {
      document.dispatchEvent(new CustomEvent(`sofiati:form-${name}`, {
        detail: { form, ...detail }
      }));
    };

    const setState = (nextState, message, role = 'status') => {
      form.dataset.formState = nextState;
      form.toggleAttribute('aria-busy', nextState === 'loading');
      if (stateNodes.length) {
        let active = null;
        stateNodes.forEach((node) => {
          const selected = node.dataset.formState === nextState;
          node.hidden = !selected;
          if (selected) active = node;
        });
        if (active) {
          active.setAttribute('role', role);
          active.setAttribute('aria-live', role === 'alert' ? 'assertive' : 'polite');
          active.tabIndex = -1;
          if (!active.textContent.trim() && message) active.textContent = message;
        }
        return active;
      }
      if (status) {
        status.hidden = !message;
        status.setAttribute('role', role);
        status.setAttribute('aria-live', role === 'alert' ? 'assertive' : 'polite');
        status.textContent = message || '';
      }
      return status;
    };

    const setSubmitting = (submitting) => {
      qsa('button[type="submit"], input[type="submit"]', form).forEach((button) => {
        if (!button.dataset.sfOriginalLabel) button.dataset.sfOriginalLabel = button.value || button.textContent || '';
        button.disabled = submitting;
        if (button.tagName === 'INPUT') button.value = submitting ? copy.loading : button.dataset.sfOriginalLabel;
        else button.textContent = submitting ? copy.loading : button.dataset.sfOriginalLabel;
      });
    };

    const configureEndpoint = (data) => {
      const endpoint = data?.forms?.endpoint || form.getAttribute('action') || '';
      if (/^https:\/\/formspree\.io\/f\/[a-z0-9]+$/i.test(endpoint)) {
        form.action = endpoint;
        return endpoint;
      }
      return '';
    };
    if (state.sharedData) configureEndpoint(state.sharedData);

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (form.dataset.formState === 'loading') return;
      const { firstInvalid, errorCount } = validate();
      if (firstInvalid) {
        setState('error', copy.review, 'alert');
        emitLifecycle('error', {
          errorType: 'client_validation',
          errorCount
        });
        firstInvalid.focus();
        return;
      }

      const honeypot = qs('input.sf-honeypot, input[name="website"]', form);
      if (honeypot && String(honeypot.value || '').trim()) {
        form.reset();
        setState('success', copy.success)?.focus({ preventScroll: true });
        return;
      }

      const endpoint = configureEndpoint(state.sharedData || await loadSharedData());
      if (!endpoint) {
        setState('error', copy.error, 'alert')?.focus({ preventScroll: true });
        emitLifecycle('error', {
          errorType: 'endpoint_unavailable',
          errorCount: 1
        });
        return;
      }

      emitLifecycle('submit');
      setSubmitting(true);
      setState('loading', copy.loading);
      const payload = new FormData(form);
      if (!payload.get('_subject')) {
        payload.set('_subject', isConsultation ? 'Sofiati consultation request' : 'Sofiati website contact');
      }
      try {
        const response = await fetch(endpoint, {
          method: 'POST',
          body: payload,
          headers: { Accept: 'application/json' }
        });
        if (!response.ok) throw new Error(`Form submission failed (${response.status})`);
        form.reset();
        fields.forEach(clearFieldError);
        setState('success', copy.success)?.focus({ preventScroll: true });
        emitLifecycle('success');
      } catch (error) {
        console.warn('[Sofiati] Form submission failed.', error);
        setState('error', copy.error, 'alert')?.focus({ preventScroll: true });
        emitLifecycle('error', {
          errorType: 'server_submission',
          errorCount: 1
        });
      } finally {
        setSubmitting(false);
      }
    });
  });
}
