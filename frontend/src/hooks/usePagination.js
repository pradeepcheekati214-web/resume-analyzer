import { useState, useCallback } from 'react';

/**
 * Simple pagination state hook.
 */
function usePagination(initialPage = 1, pageSize = 10) {
  const [page, setPage]   = useState(initialPage);
  const [total, setTotal] = useState(0);

  const totalPages = Math.ceil(total / pageSize);

  const next     = useCallback(() => setPage((p) => Math.min(p + 1, totalPages)), [totalPages]);
  const prev     = useCallback(() => setPage((p) => Math.max(p - 1, 1)), []);
  const goTo     = useCallback((p) => setPage(Math.max(1, Math.min(p, totalPages))), [totalPages]);
  const reset    = useCallback(() => setPage(1), []);

  return { page, setPage, total, setTotal, totalPages, next, prev, goTo, reset };
}

export default usePagination;
