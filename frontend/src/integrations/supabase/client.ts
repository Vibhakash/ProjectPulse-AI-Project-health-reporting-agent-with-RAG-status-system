/**
 * Local mock auth client — replaces Supabase auth so the app works
 * fully offline without any Supabase project.
 *
 * Credentials are stored in localStorage under "mock_auth_users" (a JSON map
 * of email → hashed password) and "mock_auth_session" for the active session.
 *
 * The exported `supabase` object exposes only the `auth` surface used by
 * auth.tsx and _authenticated.tsx:
 *   supabase.auth.getSession()
 *   supabase.auth.onAuthStateChange(callback)
 *   supabase.auth.signInWithPassword({ email, password })
 *   supabase.auth.signUp({ email, password })
 *   supabase.auth.signOut()
 */

const USERS_KEY = "mock_auth_users";
const SESSION_KEY = "mock_auth_session";

type MockUser = { id: string; email: string };
type MockSession = { user: MockUser; access_token: string };

// ── Tiny deterministic "hash" (NOT cryptographic – demo only) ──────────────
function simpleHash(s: string): string {
  let h = 5381;
  for (let i = 0; i < s.length; i++) h = ((h << 5) + h) ^ s.charCodeAt(i);
  return (h >>> 0).toString(16);
}

function getUsers(): Record<string, string> {
  try {
    return JSON.parse(localStorage.getItem(USERS_KEY) ?? "{}");
  } catch {
    return {};
  }
}

function saveUsers(users: Record<string, string>) {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

function getSession(): MockSession | null {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY) ?? "null");
  } catch {
    return null;
  }
}

function saveSession(session: MockSession | null) {
  if (session) {
    localStorage.setItem(SESSION_KEY, JSON.stringify(session));
  } else {
    localStorage.removeItem(SESSION_KEY);
  }
}

// ── Listeners (mirrors Supabase onAuthStateChange) ─────────────────────────
type AuthChangeCallback = (event: string, session: MockSession | null) => void;
const listeners: Set<AuthChangeCallback> = new Set();

function emit(event: string, session: MockSession | null) {
  listeners.forEach((cb) => cb(event, session));
}

// ── Auth methods ────────────────────────────────────────────────────────────
async function signInWithPassword({ email, password }: { email: string; password: string }) {
  const users = getUsers();
  const key = email.toLowerCase().trim();
  const hash = simpleHash(password);

  if (!users[key]) {
    return { data: null, error: new Error("No account found for that email. Please sign up first.") };
  }
  if (users[key] !== hash) {
    return { data: null, error: new Error("Incorrect password.") };
  }

  const session: MockSession = {
    user: { id: simpleHash(key), email: key },
    access_token: `local_${simpleHash(key + Date.now())}`,
  };
  saveSession(session);
  emit("SIGNED_IN", session);
  return { data: { session }, error: null };
}

async function signUp({ email, password }: { email: string; password: string; options?: unknown }) {
  const users = getUsers();
  const key = email.toLowerCase().trim();
  const hash = simpleHash(password);

  // Allow re-registering same email (just update password silently)
  users[key] = hash;
  saveUsers(users);

  const session: MockSession = {
    user: { id: simpleHash(key), email: key },
    access_token: `local_${simpleHash(key + Date.now())}`,
  };
  saveSession(session);
  emit("SIGNED_IN", session);
  return { data: { session, user: session.user }, error: null };
}

async function signOut() {
  saveSession(null);
  emit("SIGNED_OUT", null);
  return { error: null };
}

async function getSessionFn() {
  const session = getSession();
  return { data: { session }, error: null };
}

function onAuthStateChange(callback: AuthChangeCallback) {
  listeners.add(callback);
  // Fire immediately with current state
  const current = getSession();
  setTimeout(() => callback(current ? "SIGNED_IN" : "SIGNED_OUT", current), 0);
  return {
    data: {
      subscription: {
        unsubscribe() {
          listeners.delete(callback);
        },
      },
    },
  };
}

async function getUser() {
  const session = getSession();
  return { data: { user: session?.user ?? null }, error: null };
}

// ── Exported supabase mock ─────────────────────────────────────────────────
export const supabase = {
  auth: {
    getSession: getSessionFn,
    getUser,
    onAuthStateChange,
    signInWithPassword,
    signUp,
    signOut,
  },
} as unknown as import("@supabase/supabase-js").SupabaseClient;
