import { account, downloadCsv, request } from './api.js';
import { mountDateRange } from './date-range.js';
let page = 1;
const picker = document.querySelector('#account');
const status = document.querySelector('#status');
picker.value = account();
const session = await (await request('/api/session')).json();
const dates = mountDateRange(document.querySelector('#dates'), session.today, filtersChanged);

function filters() {
  return { ...dates.values(), status: status.value };
}

function filtersChanged() {
  page = 1;
  load();
}

async function load() {
  document.querySelector('#error').textContent = '';
  document.querySelector('#rows').replaceChildren();
  try {
    const data = await (await request('/api/appointments', { ...filters(), page })).json();
    for (const row of data.items) {
      const tr = document.createElement('tr');
      for (const key of ['id', 'name', 'email', 'starts_at', 'status']) {
        const td = document.createElement('td'); td.textContent = row[key]; tr.append(td);
      }
      document.querySelector('#rows').append(tr);
    }
    document.querySelector('#summary').textContent = `共 ${data.total} 条预约`;
    document.querySelector('#page').textContent = `第 ${page} 页`;
    document.querySelector('#previous').disabled = page === 1;
    document.querySelector('#next').disabled = page * data.page_size >= data.total;
  } catch (error) {
    document.querySelector('#error').textContent = error.message;
    document.querySelector('#summary').textContent = '';
  }
}
picker.onchange = () => { sessionStorage.setItem('account', picker.value); page = 1; load(); };
status.onchange = filtersChanged;
document.querySelector('#previous').onclick = () => { page--; load(); };
document.querySelector('#next').onclick = () => { page++; load(); };
document.querySelector('#export').onclick = async () => {
  document.querySelector('#error').textContent = '';
  try { await downloadCsv('/api/appointments/export', filters(), 'appointments.csv'); }
  catch (error) { document.querySelector('#error').textContent = error.message; }
};
load();
