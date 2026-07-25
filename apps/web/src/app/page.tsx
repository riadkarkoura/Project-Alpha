import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-6 px-8 py-32 text-center">
      <h1 className="text-4xl font-semibold tracking-tight">Project Alpha</h1>
      <p className="max-w-md text-lg text-muted-foreground">
        The AI-powered research platform for discovering, evaluating, and validating profitable
        ecommerce opportunities through data-driven analysis.
      </p>
      <Button asChild size="lg">
        <Link href="/projects">Open Workspace</Link>
      </Button>
    </div>
  );
}
