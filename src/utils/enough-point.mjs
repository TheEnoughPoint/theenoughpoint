export function cents(value) {
  const s = String(value).trim().replace(/^\./, '0.');
  if (!s) return 0;
  if (!/^\d+(\.\d{0,2})?$/.test(s)) throw new Error('Enter a positive amount with at most two decimal places.');
  const [whole, fraction = ''] = s.split('.');
  const amount = Number(whole) * 100 + Number(fraction.padEnd(2, '0'));
  if (!Number.isSafeInteger(amount) || amount > 100000000000) throw new Error('Enter an amount below S$1 billion.');
  return amount;
}
export function calculate(income, expenses) {
  const current = income.reduce((sum, row) => sum + cents(row.amount), 0);
  const continuing = income.reduce((sum, row) => sum + (row.continues ? cents(row.amount) : 0), 0);
  const outgoing = expenses.reduce((sum, row) => sum + cents(row.amount), 0);
  return { current, continuing, outgoing, currentBalance: current - outgoing, withoutWorkBalance: continuing - outgoing };
}
