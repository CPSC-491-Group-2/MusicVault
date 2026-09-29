"use client";

import { useEffect, useState } from "react";

import { getHealth } from "../services/api";
import { HealthResponse } from "../types/api";

export default function HealthStatus() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function checkHealth() {
      try {
        const result = await getHealth();
        setHealth(result);
      } catch {
        setError("Could not connect to backend.");
      }
    }

    checkHealth();
  }, []);

  if (error) {
    return <p>{error}</p>;
  }

  if (!health) {
    return <p>Checking backend...</p>;
  }

  return (
    <div>
      <h2>Backend Status</h2>
      <p>Service: {health.service}</p>
      <p>Status: {health.status}</p>
    </div>
  );
}