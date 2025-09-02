import React from "react"
import { createRoot } from "react-dom/client"
import App from "./App"

function mount(selector: string) {
  const el = document.querySelector<HTMLElement>(selector)
  if (!el) return
  const propsAttr = el.getAttribute("data-props")
  const props = propsAttr ? JSON.parse(propsAttr) : {}
  const root = createRoot(el)
  root.render(<App {...props} />)
  // Simple smoke flag for debugging if needed:
  ;(window as any).__ISLAND_OK__ = true
}

mount("#react-hello")
