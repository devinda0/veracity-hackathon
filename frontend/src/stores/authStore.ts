import { create } from 'zustand';

interface AuthUser {
  id: string;
  email: string;
  name: string;
}

interface AuthStore {
  token: string | null;
  user: AuthUser | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  hydrate: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  token: null,
  user: null,
  loading: false,
  error: null,

  hydrate: () => {
    const token = localStorage.getItem('token');
    const userRaw = localStorage.getItem('user');
    if (token && userRaw) {
      try {
        const user = JSON.parse(userRaw) as AuthUser;
        set({ token, user });
      } catch {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
  },

  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const payload = (await res.json().catch(() => ({}))) as { detail?: string };
        throw new Error(payload.detail ?? 'Invalid credentials');
      }

      const data = (await res.json()) as { access_token: string; expires_in: number };
      localStorage.setItem('token', data.access_token);

      // Fetch user info
      const meRes = await fetch('/api/v1/auth/status', {
        headers: { Authorization: `Bearer ${data.access_token}` },
      });
      // auth/status doesn't return user details, so we decode the JWT payload
      const parts = data.access_token.split('.');
      let user: AuthUser = { id: '', email, name: email };
      if (parts.length === 3) {
        try {
          const payload = JSON.parse(atob(parts[1])) as { sub?: string; email?: string };
          user = { id: payload.sub ?? '', email: payload.email ?? email, name: email };
        } catch {
          // keep defaults
        }
      }
      void meRes; // meRes not needed beyond confirming token is valid

      localStorage.setItem('user', JSON.stringify(user));
      set({ token: data.access_token, user, loading: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Login failed', loading: false });
      throw err;
    }
  },

  register: async (name, email, password) => {
    set({ loading: true, error: null });
    try {
      const res = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password }),
      });

      if (!res.ok) {
        const payload = (await res.json().catch(() => ({}))) as { detail?: string };
        throw new Error(payload.detail ?? 'Registration failed');
      }

      // Auto-login after register
      set({ loading: false });
      const store = useAuthStore.getState();
      await store.login(email, password);
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Registration failed', loading: false });
      throw err;
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({ token: null, user: null });
  },
}));
