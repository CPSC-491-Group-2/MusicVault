"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { TextField } from "@/components/ui/TextField";

export function ErrorField() {
  const [submits, setSubmits] = useState(0);

  return (
    <form
      noValidate
      onSubmit={(event) => {
        event.preventDefault();
        setSubmits((count) => count + 1);
      }}
      className="flex flex-col gap-4"
    >
      <TextField
        label="Email"
        type="email"
        error={submits === 0 ? undefined : "Enter your email"}
        errorKey={submits}
      />
      <Button variant="primary" size="md" type="submit" className="self-start">
        Submit
      </Button>
    </form>
  );
}
