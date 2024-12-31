import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

function PromptPage() {
  const [prompt, setPrompt] = useState("");
  const navigate = useNavigate();

  const promptId = "67739dbfd14c8c402b258d77";

  const fetchPrompt = async () => {
    try {
      const response = await fetch(
        `http://172.16.30.100:6743/app/getprompt?id=${promptId}`,
        {
          method: "GET",
        }
      );
      const resp = await response.json();
      setPrompt(resp?.prompt);
    } catch (err) {
      console.error("Error fetching prompt:", err);
    }
  };

  const updatePrompt = async () => {
    try {
      const response = await fetch(
        `http://172.16.30.100:6743/app/editprompt?id=${promptId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ prompt }),
        }
      );

      if (response.ok) {
        console.log("Prompt updated successfully");
      } else {
        console.error("Error updating prompt:", response.statusText);
      }
    } catch (err) {
      console.error("Error updating prompt:", err);
    }
  };

  useEffect(() => {
    fetchPrompt();
  }, []);

  const handleSubmit = () => {
    updatePrompt();
  };

  return (
    <div className='App'>
      <div className='search-container'>
        <textarea
          type='text'
          placeholder='Edit Prompt'
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />
        <button onClick={handleSubmit}>Update and Send</button>
      </div>
    </div>
  );
}

export default PromptPage;
