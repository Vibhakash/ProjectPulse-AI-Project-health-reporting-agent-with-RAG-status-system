import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { AppShell } from "@/components/app-shell";
import { useRouter } from "@tanstack/react-router";

export const Route = createFileRoute("/_authenticated")({
  // Session check happens client-side (SSR-off gate).
  component: Gate,
});

function Gate() {
  const router = useRouter();
  const [status, setStatus] = useState<"checking" | "signed-in" | "signed-out">("checking");

  useEffect(() => {
    let mounted = true;
    supabase.auth.getSession().then(({ data }) => {
      if (!mounted) return;
      setStatus(data.session ? "signed-in" : "signed-out");
    });
    const { data: sub } = supabase.auth.onAuthStateChange((_e, s) => {
      setStatus(s ? "signed-in" : "signed-out");
    });
    return () => {
      mounted = false;
      sub.subscription.unsubscribe();
    };
  }, []);

  useEffect(() => {
    if (status === "signed-out") {
      const redirectTo = window.location.pathname + window.location.search;
      router.navigate({ to: "/auth", search: { redirect: redirectTo }, replace: true });
    }
  }, [status, router]);

  if (status !== "signed-in") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background text-muted-foreground text-sm">
        Checking session…
      </div>
    );
  }
  return <AppShell />;
}