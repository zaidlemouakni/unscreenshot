"""common.py: connected components, with and without scipy."""
import unittest
from collections import deque

import numpy as np

import helpers  # noqa: F401 (puts the scripts on sys.path)
from common import _label_runs, label, objects


def reference(mask):
    """Plain breadth-first 8-connected labelling."""
    h, w = mask.shape
    lab = np.zeros((h, w), dtype=np.int32)
    n = 0
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not lab[y, x]:
                n += 1
                lab[y, x] = n
                q = deque([(y, x)])
                while q:
                    cy, cx = q.popleft()
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not lab[ny, nx]:
                                lab[ny, nx] = n
                                q.append((ny, nx))
    return lab, n


def partition(lab):
    groups = {}
    for i, v in enumerate(lab.ravel().tolist()):
        if v:
            groups.setdefault(v, []).append(i)
    return sorted(tuple(g) for g in groups.values())


class LabelTest(unittest.TestCase):
    def check(self, mask):
        lab, n = _label_runs(mask)
        ref, rn = reference(mask)
        self.assertEqual(n, rn)
        self.assertEqual(partition(lab), partition(ref))
        self.assertTrue(((lab > 0) == mask).all())
        if n:
            self.assertEqual(sorted(np.unique(lab[lab > 0]).tolist()), list(range(1, n + 1)))
        lab2, n2 = label(mask)  # scipy when installed, else the same fallback
        self.assertEqual(n2, rn)
        self.assertEqual(partition(lab2), partition(ref))

    def test_random_masks(self):
        rng = np.random.default_rng(7)
        for density in (0.05, 0.3, 0.5, 0.7):
            for shape in ((1, 1), (1, 17), (13, 1), (23, 31), (40, 9)):
                with self.subTest(density=density, shape=shape):
                    self.check(rng.random(shape) < density)

    def test_diagonals_and_u_shapes(self):
        self.check(np.eye(6, dtype=bool))                    # one diagonal component
        self.check(np.fliplr(np.eye(6, dtype=bool)))
        u = np.zeros((6, 7), dtype=bool)
        u[:, 0] = u[:, 6] = u[5, :] = True                   # arms merge only at the bottom
        self.check(u)
        comb = np.zeros((5, 9), dtype=bool)
        comb[0, :] = True
        comb[:, ::2] = True                                  # teeth joined by the top bar
        self.check(comb)

    def test_empty_and_full(self):
        self.check(np.zeros((5, 5), dtype=bool))
        self.check(np.ones((5, 5), dtype=bool))

    def test_objects(self):
        m = np.zeros((10, 12), dtype=bool)
        m[1:3, 2:6] = True
        m[6, 9] = True
        lab, n = label(m)
        boxes = sorted(o[1:] for o in objects(lab, n))
        self.assertEqual(boxes, [(2, 1, 5, 2, 8), (9, 6, 9, 6, 1)])


if __name__ == '__main__':
    unittest.main()
