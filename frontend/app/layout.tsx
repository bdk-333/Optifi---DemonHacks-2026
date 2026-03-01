import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "OptiFi",
  description: "AI financial decision assistant",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body className="bg-zinc-950 text-zinc-100 antialiased" style={{ minHeight: "100vh" }}>
        {children}
      </body>
    </html>
  )
}
