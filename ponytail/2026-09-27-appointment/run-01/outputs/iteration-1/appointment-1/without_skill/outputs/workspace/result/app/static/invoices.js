import { request, downloadCsv } from './api.js';
import { mountDateRange } from './date-range.js';
const session = await (await request('/api/session')).json();
const dates = mountDateRange(document.querySelector('#dates'), session.today);
document.querySelector('#export').onclick = async () => {
  document.querySelector('#error').textContent = '';
  try { await downloadCsv('/api/invoices/export', dates.values(), 'invoices.csv'); }
  catch (error) { document.querySelector('#error').textContent = error.message; }
};
