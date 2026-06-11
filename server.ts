import express from "express";
import path from "path";
import dotenv from "dotenv";
import { createServer as createViteServer } from "vite";
import { GoogleGenAI, Type } from "@google/genai";
// @ts-ignore
import pdfParse from "pdf-parse";
import mammoth from "mammoth";

dotenv.config();

const app = express();
const PORT = 3000;

// Set up JSON body parser with a larger limit to accommodate base64 documents
app.use(express.json({ limit: "25mb" }));

// Lazy initializer for Gemini client to prevent crash on startup if key is missing
let aiClient: GoogleGenAI | null = null;

function getGeminiClient(): GoogleGenAI {
  if (!aiClient) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      throw new Error("GEMINI_API_KEY environment variable is required. Please set it in the Settings > Secrets panel of AI Studio.");
    }
    aiClient = new GoogleGenAI({
      apiKey,
      httpOptions: {
        headers: {
          "User-Agent": "aistudio-build",
        },
      },
    });
  }
  return aiClient;
}

// REST API endpoint to parse uploaded files directly to plain text
app.post("/api/parse", async (req, res) => {
  try {
    const { fileContent, fileName } = req.body;
    if (!fileContent) {
      return res.status(400).json({ error: "No file content provided" });
    }

    const buffer = Buffer.from(fileContent, "base64");
    let extractedText = "";

    const extension = fileName ? path.extname(fileName).toLowerCase() : "";

    if (extension === ".pdf") {
      const parsed = await pdfParse(buffer);
      extractedText = parsed.text || "";
    } else if (extension === ".docx") {
      const parsed = await mammoth.extractRawText({ buffer });
      extractedText = parsed.value || "";
    } else {
      // Treat as plain text UTF-8
      extractedText = buffer.toString("utf-8");
    }

    res.json({ text: extractedText.trim() });
  } catch (error: any) {
    console.error("File extraction error:", error);
    res.status(500).json({ error: "Failed to extract text from file: " + error.message });
  }
});

// REST API endpoint to run the AI resume analysis
app.post("/api/analyze", async (req, res) => {
  try {
    const { resumeText, jobDescription } = req.body;

    if (!resumeText || !resumeText.trim()) {
      return res.status(400).json({ error: "Resume text is empty or missing" });
    }
    if (!jobDescription || !jobDescription.trim()) {
      return res.status(400).json({ error: "Job description is empty or missing" });
    }

    const ai = getGeminiClient();

    const systemInstruction = `You are a Senior Talent Acquisition Manager, Technical Recruiter, and Applicant Tracking System (ATS) compatibility engineer. 
Your task is to analyze the user's resume text relative to the target Job Description (JD). 
Evaluate candidate credentials, structural layout, experience hierarchy, actionable gaps, skill keyword match, and ATS optimization elements.
Provide constructive, objective, and highly professional advice. 
You must respond strictly with a valid JSON object matching the requested schema.`;

    const userPrompt = `Target Job Description:
${jobDescription}

Candidate Resume:
${resumeText}

Analyze this candidate and respond with a complete, structured analysis using the defined response schema. Ensure the match score is a realistic percentage (0-100) reflecting actual skill matching and experience levels. Give precise keywords that are matched, and key high-priority missing items. Detailed analysis should incorporate ATS formatting suggestions in visual Markdown.`;

    const responseSchema = {
      type: Type.OBJECT,
      properties: {
        match_percentage: {
          type: Type.INTEGER,
          description: "ATS alignment & keyword match percentage from 0 to 100",
        },
        matched_skills: {
          type: Type.ARRAY,
          items: { type: Type.STRING },
          description: "Core matching skills/keywords present in both resume and JD",
        },
        missing_skills: {
          type: Type.ARRAY,
          items: { type: Type.STRING },
          description: "Important keywords or skills listed in the JD that are not found in the resume",
        },
        strengths: {
          type: Type.ARRAY,
          items: { type: Type.STRING },
          description: "Key professional highlights and strong matching features found",
        },
        improvements: {
          type: Type.ARRAY,
          items: { type: Type.STRING },
          description: "Concrete items of improvement, layout suggestions, or detail-additions",
        },
        suggested_role: {
          type: Type.STRING,
          description: "A recommended professional job/role title based on their skills and target JD",
        },
        detailed_analysis: {
          type: Type.STRING,
          description: "Comprehensive feedback in formatted Markdown, highlighting layout changes, tailored keywords, and ATS optimization advice",
        }
      },
      required: [
        "match_percentage",
        "matched_skills",
        "missing_skills",
        "strengths",
        "improvements",
        "suggested_role",
        "detailed_analysis"
      ]
    };

    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: userPrompt,
      config: {
        systemInstruction,
        responseMimeType: "application/json",
        responseSchema,
        temperature: 0.2, // Low temperature for consistent ATS analysis
      },
    });

    const textOutput = response.text;
    if (!textOutput) {
      throw new Error("No response output returned from Gemini API");
    }

    try {
      const jsonResult = JSON.parse(textOutput.trim());
      res.json(jsonResult);
    } catch (parseErr) {
      console.error("Gemini output parsing error:", textOutput);
      res.status(502).json({
        error: "Received invalid JSON format from AI model.",
        rawOutput: textOutput
      });
    }

  } catch (error: any) {
    console.error("Gemini analysis error:", error);
    res.status(500).json({ error: error.message || "Internal Server Error occurred during AI analysis." });
  }
});

// Setup Vite Dev Middleware / Static Build serving
async function setupServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`AI Resume Analyzer backend listening on http://0.0.0.0:${PORT}`);
  });
}

setupServer();
