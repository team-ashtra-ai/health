#!/usr/bin/env node

import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';

const budgets = JSON.parse(await readFile(resolve('config/performance/budget.json'), 'utf8'));
const report = JSON.parse(await readFile(resolve('reports/performance/validation.json'), 'utf8'));
const failures = [];
const warnings = [];

function check(condition, message, severity = 'failure') {
  if (condition) return;
  (severity === 'warning' ? warnings : failures).push(message);
}

for (const group of report.groups) {
  const lab = budgets.laboratory[group.profile];
  const summary = group.summary;
  const pageBudget = budgets.pageTypes[group.route];
  check(
    summary.performance.median >= lab.performanceMedianMinimum,
    `${group.route} ${group.profile}: performance median ${summary.performance.median} < ${lab.performanceMedianMinimum}`
  );
  check(
    summary.performance.min >= lab.performanceRunMinimum,
    `${group.route} ${group.profile}: minimum performance ${summary.performance.min} < ${lab.performanceRunMinimum}`
  );
  check(
    summary.lcpMs.median <= lab.lcpMedianMaximum,
    `${group.route} ${group.profile}: LCP ${summary.lcpMs.median} ms > ${lab.lcpMedianMaximum} ms`
  );
  check(
    summary.fcpMs.median <= lab.fcpMedianMaximum,
    `${group.route} ${group.profile}: FCP ${summary.fcpMs.median} ms > ${lab.fcpMedianMaximum} ms`
  );
  check(
    summary.tbtMs.median <= lab.tbtMedianMaximum,
    `${group.route} ${group.profile}: TBT ${summary.tbtMs.median} ms > ${lab.tbtMedianMaximum} ms`
  );
  check(
    summary.cls.median <= lab.clsMedianMaximum,
    `${group.route} ${group.profile}: CLS ${summary.cls.median} > ${lab.clsMedianMaximum}`
  );
  check(
    summary.script.median <= budgets.resourceBudgets.initialJavaScriptMaximum,
    `${group.route} ${group.profile}: JS transfer ${summary.script.median} bytes exceeds budget`
  );
  check(
    summary.stylesheet.median <= budgets.resourceBudgets.initialCssMaximum,
    `${group.route} ${group.profile}: CSS transfer ${summary.stylesheet.median} bytes exceeds budget`
  );
  check(
    summary.font.median <= budgets.resourceBudgets.criticalFontMaximum,
    `${group.route} ${group.profile}: font transfer ${summary.font.median} bytes exceeds budget`
  );
  if (pageBudget) {
    check(
      summary.totalTransferBytes.median <= pageBudget.totalTransferMaximum,
      `${group.route} ${group.profile}: transfer ${summary.totalTransferBytes.median} bytes exceeds ${pageBudget.totalTransferMaximum}`,
      'warning'
    );
    check(
      summary.requestCount.median <= pageBudget.requestMaximum,
      `${group.route} ${group.profile}: ${summary.requestCount.median} requests exceeds ${pageBudget.requestMaximum}`,
      'warning'
    );
  }
}

console.log(JSON.stringify({
  passed: failures.length === 0,
  checkedGroups: report.groups.length,
  failures,
  warnings
}, null, 2));
if (failures.length) process.exitCode = 1;
