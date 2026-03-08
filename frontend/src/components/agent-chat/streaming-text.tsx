"use client";

import { useEffect, useState } from "react";

interface StreamingTextProps {
  text: string;
  isStreaming: boolean;
}

export function StreamingText({ text, isStreaming }: StreamingTextProps) {
  const [displayText, setDisplayText] = useState("");

  useEffect(() => {
    setDisplayText(text);
  }, [text]);

  return (
    <span>
      {displayText}
      {isStreaming && (
        <span className="inline-block w-0.5 h-4 bg-current ml-0.5 animate-pulse" />
      )}
    </span>
  );
}
