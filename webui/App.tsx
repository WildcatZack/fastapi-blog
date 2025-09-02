import React from "react"

type Props = {
  message?: string
}

export default function App({ message = "Hello from React Island!" }: Props) {
  const [count, setCount] = React.useState(0)

  return (
    <div
      style={{
        padding: "12px 16px",
        borderRadius: "12px",
        border: "1px solid #ddd",
        boxShadow: "0 2px 8px rgba(0,0,0,.05)",
        background: "white",
      }}
    >
      <strong>React Island!:</strong> {message}
      <div style={{ marginTop: 8 }}>
        <button onClick={() => setCount((c) => c + 1)}>Clicks: {count}</button>
      </div>
    </div>
  )
}
