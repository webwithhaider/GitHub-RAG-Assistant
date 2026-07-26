import "./globals.css";

export const metadata = {
  title: "Codebase RAG Assistant",
  description: "Ask questions about any GitHub repository.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
