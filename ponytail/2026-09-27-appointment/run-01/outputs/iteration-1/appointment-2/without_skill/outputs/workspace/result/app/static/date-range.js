export function mountDateRange(container, today, onChange = () => {}) {
  container.innerHTML = '<label>开始日期 <input type="date" name="start"></label> <label>结束日期 <input type="date" name="end"></label> <button type="button" data-days="7">最近7天</button> <button type="button" data-clear>全部日期</button>';
  const start = container.querySelector('[name=start]');
  const end = container.querySelector('[name=end]');
  container.querySelector('[data-days]').onclick = () => {
    const day = new Date(today + 'T00:00:00Z');
    day.setUTCDate(day.getUTCDate() - 6);
    start.value = day.toISOString().slice(0, 10); end.value = today; onChange();
  };
  container.querySelector('[data-clear]').onclick = () => { start.value = ''; end.value = ''; onChange(); };
  start.onchange = end.onchange = onChange;
  return { values: () => ({ start: start.value, end: end.value }) };
}
