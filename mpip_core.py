"""
mpip_core.py
Modular-Polynomial Identity Proof (MPIP) Framework Core Logic
"""

import numpy as np
import hashlib

class MPIPFramework:
    def __init__(self, target_level="Level2"):
        """Initialize parameters based on target security level."""
        if target_level == "Level2":
            self.N = 256
            self.q = 8380417
            self.K = 4
            self.L = 4
            self.eta = 2
            self.gamma = 131072
            self.tau = 39
            self.beta = self.tau * self.eta
        else:
            raise ValueError("Unsupported target level.")

        # Simulate a globally shared public matrix A
        self.A = np.random.randint(0, self.q, size=(self.K, self.L, self.N), dtype=np.int64)

    def _poly_mul(self, a, b):
        """Helper: Polynomial multiplication in R_q."""
        conv = np.convolve(a, b)
        result = np.zeros(self.N, dtype=np.int64)
        for i in range(len(conv)):
            if i < self.N:
                result[i] = (result[i] + conv[i]) % self.q
            else:
                result[i % self.N] = (result[i % self.N] - conv[i]) % self.q
        return result

    def _matrix_vector_mul(self, Matrix, vector):
        """Helper: Matrix-vector multiplication over R_q."""
        result = np.zeros((Matrix.shape[0], self.N), dtype=np.int64)
        for i in range(Matrix.shape[0]):
            for j in range(Matrix.shape[1]):
                result[i] = (result[i] + self._poly_mul(Matrix[i, j], vector[j])) % self.q
        return result

    def _hash_to_challenge(self, w, mu):
        """Simulates SHAKE-128 XOF hash to generate a sparse challenge polynomial."""
        w_high_bits = (w >> 4).astype(np.uint8).tobytes()
        hash_input = w_high_bits + mu.encode('utf-8')
        digest = hashlib.shake_128(hash_input).digest(self.N)

        c = np.zeros(self.N, dtype=np.int64)
        indices = np.argsort(list(digest))[:self.tau]
        for idx in indices:
            c[idx] = 1 if digest[idx] % 2 == 0 else -1
        return c

    def phase_1_key_generation(self):
        """PHASE I: Generates Secret Identity and Public Credential."""
        s = np.random.randint(-self.eta, self.eta + 1, size=(self.L, self.N), dtype=np.int64)
        e = np.random.randint(-self.eta, self.eta + 1, size=(self.K, self.N), dtype=np.int64)
        t = (self._matrix_vector_mul(self.A, s) + e) % self.q
        return (s, e), t

    def phase_2_proof_generation(self, s, mu):
        """PHASE II: Proof Generation with the Modular Guard rejection loop."""
        attempts = 0
        safe_bound = self.gamma - self.beta

        while True:
            attempts += 1
            y = np.random.randint(-self.gamma, self.gamma + 1, size=(self.L, self.N), dtype=np.int64)
            w = self._matrix_vector_mul(self.A, y)
            c = self._hash_to_challenge(w, mu)

            cs = np.zeros((self.L, self.N), dtype=np.int64)
            for i in range(self.L):
                cs[i] = self._poly_mul(c, s[i])
                cs[i] = np.where(cs[i] > self.q // 2, cs[i] - self.q, cs[i])

            z = y + cs

            # THE MODULAR GUARD
            if np.max(np.abs(z)) <= safe_bound:
                return (z, c), attempts

    def phase_3_verification(self, z, c, t, mu):
        """PHASE III: Verifies the Proof tuple."""
        safe_bound = self.gamma - self.beta

        if np.max(np.abs(z)) > safe_bound:
            return False

        Az = self._matrix_vector_mul(self.A, z)
        ct = np.zeros((self.K, self.N), dtype=np.int64)
        for i in range(self.K):
            ct[i] = self._poly_mul(c, t[i])

        w_prime = (Az - ct) % self.q
        c_prime = self._hash_to_challenge(w_prime, mu)

        return np.array_equal(c, c_prime)
