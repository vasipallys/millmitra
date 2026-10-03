export function unwrapList(payload, keys = []) {
  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== 'object') return [];
  for (const key of keys) {
    if (Array.isArray(payload[key])) return payload[key];
  }
  return [];
}

export function remainingPaddyKg(lots) {
  return lots.reduce((sum, lot) => {
    const remaining = lot.remaining_quantity ?? lot.quantity ?? 0;
    return sum + (Number(remaining) || 0);
  }, 0);
}

export function productStockKg(products) {
  return products.reduce((sum, item) => (
    sum + (Number(item.quantity ?? item.current_stock ?? item.remaining_quantity) || 0)
  ), 0);
}

export function isOpenBatch(batch) {
  const status = String(batch?.status || '').toLowerCase();
  return ['in_progress', 'started', 'paused'].includes(status);
}

export function isPlannedBatch(batch) {
  return String(batch?.status || '').toLowerCase() === 'planned';
}

export function isUnpaidInvoice(invoice) {
  const status = String(invoice?.status || '').toLowerCase();
  if (['paid', 'cancelled', 'void'].includes(status)) return false;
  return ['pending', 'overdue', 'partial', 'unpaid', ''].includes(status);
}

export function suggestMillStep({ paddyLots = [], batches = [], products = [], invoices = [] } = {}) {
  const paddyKg = remainingPaddyKg(paddyLots);
  const openBatches = batches.filter(isOpenBatch);
  const plannedBatches = batches.filter(isPlannedBatch);
  const productKg = productStockKg(products);
  const unpaid = invoices.filter(isUnpaidInvoice);

  if (paddyKg <= 0 && !openBatches.length && !plannedBatches.length) {
    return {
      step: 0,
      title: 'Receive paddy',
      reason: 'No paddy in the godown. Start by recording a farmer lot so the mill has grain to mill.',
    };
  }
  if (openBatches.length) {
    return {
      step: 2,
      title: 'Finish the batch',
      reason: 'A batch is in progress. Record a quality test if needed, then complete it with output kg.',
    };
  }
  if (paddyKg > 0 || plannedBatches.length) {
    return {
      step: 1,
      title: 'Start a batch',
      reason: plannedBatches.length
        ? 'A planned batch is waiting. Start it so paddy is deducted and milling can be recorded.'
        : 'Paddy is available and no batch is running. Start a batch from a lot.',
    };
  }
  if (unpaid.length) {
    return {
      step: 4,
      title: 'Record payment',
      reason: `${unpaid.length} unpaid invoice${unpaid.length === 1 ? '' : 's'}. Record a collection on Finance.`,
    };
  }
  if (productKg > 0) {
    return {
      step: 3,
      title: 'Sell or invoice',
      reason: 'Rice is in product stock and there is no unpaid invoice. Create an order or invoice.',
    };
  }
  return {
    step: 0,
    title: 'Receive paddy',
    reason: 'No open mill work. Receive paddy to begin a new run.',
  };
}
