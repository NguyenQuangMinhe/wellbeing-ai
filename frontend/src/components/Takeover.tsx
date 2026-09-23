import { useState } from "react";
// TODO : Boundary?
type TakeoverKind = "crisis" | "boundary";

type SupportLink = {
  label: string;
  detail: string;
  href: string;
};

const SUPPORT_LINKS: SupportLink[] = [
  { label: "Emergency", detail: "000", href: "tel:000" },
  { label: "Lifeline Australia", detail: "13 11 14", href: "tel:131114" },
  { label: "Beyond Blue", detail: "1300 22 4636", href: "tel:1300224636" },
];

type LinkStatus = "idle" | "loading" | "error";

function SupportLinkRow({ link }: { link: SupportLink }) {
  const [status, setStatus] = useState<LinkStatus>("idle");

  async function handleCopy() {
    setStatus("loading");
    try {
      await navigator.clipboard.writeText(link.detail);
      setStatus("idle");
    } catch {
      setStatus("error");
    }
  }

    return (
    <li className="flex items-center justify-between gap-3 rounded-md border border-gray-200 bg-white px-3 py-2">
        <a
        href={link.href}
        className="flex-1 text-sm text-gray-800 underline decoration-gray-300 underline-offset-2
                    hover:text-blue-700 hover:decoration-blue-400
                    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 rounded
                    active:text-blue-900"
        >
        <span className="font-medium">{link.label}</span>
        <span className="text-gray-500"> — {link.detail}</span>
        </a>

        <button
        type="button"
        onClick={handleCopy}
        disabled={status === "loading"}
        aria-busy={status === "loading"}
        className="shrink-0 rounded px-2 py-1 text-xs font-medium text-gray-600
                    hover:bg-gray-100 hover:text-gray-800
                    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400
                    active:bg-gray-200
                    disabled:opacity-50 disabled:cursor-not-allowed"
        >
        {status === "loading"
            ? "Copying…"
            : status === "error"
            ? "Retry"
            : "Copy"}
        </button>

        {status === "error" && (
        <span role="alert" className="text-xs text-red-600">
            Couldn't copy — try selecting the number manually.
        </span>
        )}
    </li>
    );

}

export function TakeoverScreen({
  kind,
  message,
}: {
  kind: TakeoverKind;
  message: string | null;
}) {
  const heading =
    kind === "crisis"
      ? "You deserve support right now"
      : "Let's take a different approach";

  return (
    <div
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="takeover-heading"
      className="fixed inset-0 z-30 flex flex-col items-center justify-center gap-4 bg-white p-6 text-center"
    >
      <h2 id="takeover-heading" className="text-lg font-semibold text-gray-900">
        {heading}
      </h2>

      {message && (
        <p className="max-w-sm whitespace-pre-line text-sm text-gray-700">{message}</p>
      )}

      {kind === "crisis" && (
        <ul className="w-full max-w-sm space-y-2 text-left">
          {SUPPORT_LINKS.map((link) => (
            <SupportLinkRow key={link.label} link={link} />
          ))}
        </ul>
      )}

      <p className="mt-2 text-xs text-gray-400" aria-live="polite">
        This conversation has been paused. Sending messages is disabled.
      </p>
    </div>
  );
}