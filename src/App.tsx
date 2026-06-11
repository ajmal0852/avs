/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import { 
  FileText, 
  Briefcase, 
  UploadCloud, 
  CheckCircle, 
  AlertCircle, 
  Sparkles, 
  RefreshCw, 
  Search, 
  ListChecks, 
  Clipboard, 
  ArrowRight, 
  Award, 
  Cpu, 
  BookOpen,
  ArrowUpRight,
  ShieldAlert,
  HelpCircle,
  FileCheck
} from "lucide-react";
import Markdown from "react-markdown";

interface AnalysisResult {
  match_percentage: number;
  matched_skills: string[];
  missing_skills: string[];
  strengths: string[];
  improvements: string[];
  suggested_role: string;
  detailed_analysis: string;
}

export default function App() {
  const [resumeText, setResumeText] = useState<string>("");
  const [jobDescription, setJobDescription] = useState<string>("");
  const [fileName, setFileName] = useState<string>("");
  const [parsingFile, setParsingFile] = useState<boolean>(false);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [analysisStep, setAnalysisStep] = useState<number>(0);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadingSteps = [
    "Reading resume layout and formatting structures...",
    "Extracting experience hierarchy and core qualifications...",
    "Analyzing skills alignment against job description...",
    "Optimizing keyword vectors to match ATS standards...",
    "Generating actionable feedback and suggestions..."
  ];

  // Drag and drop handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = async (file: File) => {
    const validExtensions = [".pdf", ".docx", ".txt"];
    const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase();
    
    if (!validExtensions.includes(ext)) {
      setError("Supported formats are only .pdf, .docx, and .txt files");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError("File size exceeds 5MB limit");
      return;
    }

    setError(null);
    setFileName(file.name);
    setParsingFile(true);

    try {
      const reader = new FileReader();
      reader.onload = async (event) => {
        if (!event.target?.result) return;
        
        const base64Content = (event.target.result as string).split(",")[1];
        
        const response = await fetch("/api/parse", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            fileContent: base64Content,
            fileName: file.name
          })
        });

        if (!response.ok) {
          throw new Error("Failed to extract content from document");
        }

        const data = await response.json();
        setResumeText(data.text);
      };

      reader.readAsDataURL(file);
    } catch (err: any) {
      setError(err.message || "An error occurred while parsing the document.");
    } finally {
      setParsingFile(false);
    }
  };

  const runAnalysis = async () => {
    if (!resumeText.trim()) {
      setError("Please upload a resume or paste your resume text in the text area.");
      return;
    }
    if (!jobDescription.trim()) {
      setError("Please paste the target job description to match against.");
      return;
    }

    setError(null);
    setResult(null);
    setAnalyzing(true);
    setAnalysisStep(0);

    // Dynamic loading screen animation simulator
    const stepInterval = setInterval(() => {
      setAnalysisStep((prev) => {
        if (prev < loadingSteps.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 2500);

    try {
      const response = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resumeText,
          jobDescription
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to complete AI review.");
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Network issue connecting with the AI compliance server.");
    } finally {
      clearInterval(stepInterval);
      setAnalyzing(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  return (
    <div id="ai_resume_analyzer_app" className="min-h-screen bg-slate-50 font-sans text-slate-800 antialiased selection:bg-indigo-100 selection:text-indigo-900">
      
      {/* Visual Workspace Header */}
      <header className="border-b border-slate-200 bg-white shadow-sm sticky top-0 z-50">
        <div className="mx-auto max-w-7xl px-4 py-4 sm:px-6 lg:px-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-indigo-600 p-2 text-white shadow-md shadow-indigo-100">
              <Sparkles className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-slate-900">AI Resume Analyzer</h1>
              <p className="text-xs text-slate-500 font-mono">Model: Gemini-3.5-Flash (ATS-Optimized)</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 flex items-center gap-1.5 border border-slate-200">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              Workspace Active
            </div>
          </div>
        </div>
      </header>

      {/* Primary Workspace Grid */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-12 items-start">
          
          {/* LEFT COLUMN: Files, paste, and text settings (5/12 columns) */}
          <div className="lg:col-span-5 space-y-6">
            
            {/* INGESTION CARD */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-2.5 mb-4 border-b border-slate-100 pb-3">
                <FileText className="h-5 w-5 text-indigo-600 animate-pulse" />
                <h2 className="text-lg font-bold text-slate-900">1. Upload Resume</h2>
              </div>

              {/* Drag and Drop Zone */}
              <div 
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={triggerFileSelect}
                className={`group cursor-pointer rounded-xl border-2 border-dashed p-6 text-center transition-all ${
                  dragActive 
                    ? "border-indigo-600 bg-indigo-50/50" 
                    : "border-slate-300 bg-slate-50 hover:border-indigo-400 hover:bg-slate-50/50"
                }`}
              >
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={handleFileInput} 
                  className="hidden" 
                  accept=".pdf,.docx,.txt"
                />
                
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-white shadow-soft text-slate-400 group-hover:text-indigo-600 group-hover:scale-110 transition-transform">
                  {parsingFile ? (
                    <RefreshCw className="h-6 w-6 animate-spin text-indigo-600" />
                  ) : (
                    <UploadCloud className="h-6 w-6" />
                  )}
                </div>
                
                <p className="mt-3 text-sm font-semibold text-slate-700">
                  {fileName ? `Loaded: ${fileName}` : "Drag & drop file here or browse"}
                </p>
                <p className="mt-1 text-xs text-slate-500 font-medium">
                  Supports PDF, DOCX, & TXT up to 5MB
                </p>
              </div>

              {/* Edit Raw Resume Text Area */}
              <div className="mt-5 space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase tracking-wider">
                  <label htmlFor="pasted_resume_text">Or paste resume contents directly</label>
                  <span>{resumeText ? `${resumeText.length} characters` : "Empty"}</span>
                </div>
                <textarea 
                  id="pasted_resume_text"
                  rows={8}
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  placeholder="Paste complete copy of your CV or resume text..."
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm font-sans placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-slate-50/30 transition-shadow focus:shadow-sm"
                />
              </div>
            </div>

            {/* JOB DESCRIPTION CARD */}
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center gap-2.5 mb-4 border-b border-slate-100 pb-3">
                <Briefcase className="h-5 w-5 text-indigo-600" />
                <h2 className="text-lg font-bold text-slate-900">2. Target Job Description</h2>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase tracking-wider">
                  <label htmlFor="pasted_jd_text">Paste the full Role description</label>
                  <span>{jobDescription ? `${jobDescription.length} characters` : "Empty"}</span>
                </div>
                <textarea 
                  id="pasted_jd_text"
                  rows={8}
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the target job outline, requirements, or listing description..."
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm font-sans placeholder-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 bg-slate-50/30 transition-shadow focus:shadow-sm"
                />
              </div>
            </div>

            {/* ANALYZE ACTION TRIGGER */}
            <div className="space-y-3">
              <button
                id="analyze_resume_button"
                onClick={runAnalysis}
                disabled={analyzing || parsingFile}
                className={`w-full touch-manipulation py-4 px-6 rounded-xl font-bold text-white shadow-md flex items-center justify-center gap-2 transition-all cursor-pointer ${
                  analyzing || parsingFile
                    ? "bg-slate-400 cursor-not-allowed shadow-none"
                    : "bg-indigo-600 hover:bg-indigo-700 hover:shadow-lg active:scale-[98%]"
                }`}
              >
                {analyzing ? (
                  <>
                    <RefreshCw className="h-5 w-5 animate-spin" />
                    AI Processing Analysis...
                  </>
                ) : (
                  <>
                    <Cpu className="h-5 w-5" />
                    Run Compliance Match
                    <ArrowRight className="h-5 w-5" />
                  </>
                )}
              </button>

              {error && (
                <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 flex gap-3 text-rose-800 text-sm animate-shake">
                  <AlertCircle className="h-5 w-5 flex-shrink-0 text-rose-600" />
                  <p className="font-medium">{error}</p>
                </div>
              )}
            </div>

          </div>

          {/* RIGHT COLUMN: Interactive Findings & Visualization (7/12 columns) */}
          <div className="lg:col-span-7">
            
            <AnimatePresence mode="wait">
              
              {/* STATE 1: Analyzing Loading Screen */}
              {analyzing && (
                <motion.div 
                  key="analyzing_state"
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.98 }}
                  className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-md space-y-8"
                >
                  <div className="space-y-3">
                    <div className="mx-auto h-16 w-16 relative flex items-center justify-center">
                      <div className="absolute inset-0 rounded-full bg-indigo-100 animate-ping opacity-70"></div>
                      <div className="relative rounded-full bg-indigo-600 p-4 text-white">
                        <Cpu className="h-8 w-8 animate-pulse" />
                      </div>
                    </div>
                    <h3 className="text-xl font-extrabold text-slate-900">Engaging Gemini Compliance Core</h3>
                    <p className="text-sm text-slate-500 max-w-sm mx-auto">
                      Our ATS Optimization model is parsing alignment values, structure files, and metadata ratios.
                    </p>
                  </div>

                  {/* Checklist pipeline status */}
                  <div className="space-y-3 max-w-md mx-auto text-left border border-slate-100 rounded-xl p-5 bg-slate-50/50">
                    {loadingSteps.map((step, idx) => (
                      <div key={idx} className="flex items-center gap-3">
                        <div className="flex-shrink-0">
                          {analysisStep > idx ? (
                            <CheckCircle className="h-5 w-5 text-emerald-500" />
                          ) : analysisStep === idx ? (
                            <RefreshCw className="h-5 w-5 text-indigo-600 animate-spin" />
                          ) : (
                            <div className="h-4 w-4 rounded-full border-2 border-slate-300 ml-0.5"></div>
                          )}
                        </div>
                        <span className={`text-sm font-semibold transition-colors ${
                          analysisStep === idx ? "text-indigo-900 font-extrabold" : "text-slate-400"
                        }`}>
                          {step}
                        </span>
                      </div>
                    ))}
                  </div>

                  <p className="text-xs text-slate-400 font-mono animate-pulse">Running semantic comparison...</p>
                </motion.div>
              )}

              {/* STATE 2: Empty/Welcome State */}
              {!analyzing && !result && (
                <motion.div 
                  key="empty_state"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm space-y-6"
                >
                  <div className="text-center space-y-2">
                    <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
                      <FileCheck className="h-8 w-8" />
                    </div>
                    <h2 className="text-2xl font-extrabold text-slate-900 leading-tight">Match Your Resume with Direct ATS Keywords</h2>
                    <p className="text-slate-500 text-sm max-w-md mx-auto">
                      Expose gaps in keyword density, formatting structure, and structural requirements to score 100% on compliance detectors.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 border-t border-slate-100 pt-6">
                    <div className="rounded-xl bg-slate-50 p-4 border border-slate-150">
                      <div className="flex items-center gap-2 mb-1.5 text-slate-900 font-bold text-sm">
                        <Award className="h-4 w-4 text-indigo-600" />
                        Complete Compliance Score
                      </div>
                      <p className="text-xs text-slate-500 leading-relaxed font-semibold">
                        Detailed breakdown metric displaying exactly how your layout, experience text, and terms align with the recruiter’s profile specifications.
                      </p>
                    </div>

                    <div className="rounded-xl bg-slate-50 p-4 border border-slate-150">
                      <div className="flex items-center gap-2 mb-1.5 text-slate-900 font-bold text-sm">
                        <ListChecks className="h-4 w-4 text-indigo-600" />
                        Precision Keyword Tags
                      </div>
                      <p className="text-xs text-slate-500 leading-relaxed font-semibold">
                        Identify specific tools, concepts, packages, and skills listed in the job description that must be added to your experience descriptors.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-4 p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-800 font-semibold leading-relaxed">
                    <ShieldAlert className="h-5 w-5 text-amber-600 flex-shrink-0" />
                    <div>
                      <p className="font-bold">Privacy first standard:</p>
                      <p className="text-amber-700 mt-0.5">
                        Your resume files and description pastes are evaluated entirely server-side. No resume data is crawled or cached permanently.
                      </p>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* STATE 3: Results Display */}
              {!analyzing && result && (
                <motion.div 
                  key="results_state"
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  
                  {/* OVERVIEW SCORE CARD */}
                  <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                      
                      {/* Metric Score circle */}
                      <div className="flex items-center gap-5">
                        <div className="relative flex-shrink-0 flex items-center justify-center">
                          <svg className="h-28 w-28 transform -rotate-90">
                            <circle 
                              cx="56" 
                              cy="56" 
                              r="48" 
                              stroke="#f1f5f9" 
                              strokeWidth="8" 
                              fill="transparent" 
                            />
                            <motion.circle 
                              cx="56" 
                              cy="56" 
                              r="48" 
                              stroke={
                                result.match_percentage >= 75 
                                  ? "#10b981" 
                                  : result.match_percentage >= 50 
                                    ? "#f59e0b" 
                                    : "#ef4444"
                              } 
                              strokeWidth="8" 
                              fill="transparent" 
                              strokeDasharray={2 * Math.PI * 48}
                              initial={{ strokeDashoffset: 2 * Math.PI * 48 }}
                              animate={{ strokeDashoffset: (2 * Math.PI * 48) * (1 - result.match_percentage / 100) }}
                              transition={{ duration: 1.2, ease: "easeOut" }}
                            />
                          </svg>
                          <div className="absolute text-center">
                            <span className="text-3xl font-extrabold text-slate-950 font-mono">
                              {result.match_percentage}
                            </span>
                            <span className="text-xs font-bold text-slate-500 block uppercase tracking-wider">%</span>
                          </div>
                        </div>

                        <div>
                          <p className="text-xs font-semibold text-slate-500 uppercase tracking-widest leading-none mb-1">Resulting Fit Score</p>
                          <h3 className="text-xl font-black text-slate-900 leading-tight">
                            {result.match_percentage >= 75 
                              ? "Excellent Fit Alignment" 
                              : result.match_percentage >= 50 
                                ? "Solid Match with Gaps" 
                                : "Substantial Optimization Needed"}
                          </h3>
                          <div className="mt-1.5 inline-flex items-center gap-1.5 rounded-full bg-indigo-50 border border-indigo-200 px-3 py-1 text-xs font-extrabold text-indigo-700">
                            <Award className="h-3.5 w-3.5" />
                            Target Alignment: {result.suggested_role}
                          </div>
                        </div>
                      </div>

                      {/* Score control actions */}
                      <div className="flex-shrink-0 flex gap-2 w-full md:w-auto">
                        <button 
                          onClick={() => copyToClipboard(JSON.stringify(result, null, 2))}
                          className="flex-1 md:flex-none py-2 px-4 border border-slate-200 rounded-xl font-bold text-sm bg-white hover:bg-slate-50 transition-colors inline-flex items-center justify-center gap-1.5 text-slate-700 shadow-sm cursor-pointer"
                        >
                          <Clipboard className="h-4 w-4" />
                          {copied ? "Copied!" : "Copy Report"}
                        </button>
                        <button 
                          onClick={runAnalysis}
                          className="flex-1 md:flex-none py-2 px-4 bg-indigo-600 rounded-xl font-bold text-sm text-white hover:bg-indigo-700 transition-colors inline-flex items-center justify-center gap-1.5 shadow-sm cursor-pointer"
                        >
                          <RefreshCw className="h-4 w-4" />
                          Re-Analyze
                        </button>
                      </div>

                    </div>
                  </div>

                  {/* KEYWORD DIFFERENCES LISTS (COMPARATIVE BENTO) */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    
                    {/* Matched Keywords */}
                    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm flex flex-col">
                      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100 flex-shrink-0">
                        <CheckCircle className="h-4 w-4 text-emerald-500" />
                        <h4 className="font-bold text-slate-900 text-sm uppercase tracking-wide">
                          Matched Skills ({result.matched_skills.length})
                        </h4>
                      </div>
                      
                      <div className="flex-grow">
                        {result.matched_skills.length > 0 ? (
                          <div className="flex flex-wrap gap-1.5">
                            {result.matched_skills.map((skill, i) => (
                              <span 
                                key={i} 
                                className="bg-emerald-50 border border-emerald-200 px-2.5 py-1 text-xs rounded-lg font-semibold text-emerald-800"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <p className="text-xs text-slate-400 font-medium italic">No matched criteria identified.</p>
                        )}
                      </div>
                    </div>

                    {/* Missing Keywords */}
                    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm flex flex-col">
                      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-100 flex-shrink-0">
                        <AlertCircle className="h-4 w-4 text-amber-500" />
                        <h4 className="font-bold text-slate-900 text-sm uppercase tracking-wide">
                          Gaps / Missing Skills ({result.missing_skills.length})
                        </h4>
                      </div>

                      <div className="flex-grow">
                        {result.missing_skills.length > 0 ? (
                          <div className="flex flex-wrap gap-1.5">
                            {result.missing_skills.map((skill, i) => (
                              <span 
                                key={i} 
                                className="bg-amber-50 border border-amber-200 px-2.5 py-1 text-xs rounded-lg font-semibold text-amber-800"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        ) : (
                          <p className="text-xs text-emerald-600 font-medium italic">Perfect keyword coverage!</p>
                        )}
                      </div>
                    </div>

                  </div>

                  {/* STRENGTHS AND ROOT IMPROVEMENTS */}
                  <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-5">
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      
                      {/* Strengths list */}
                      <div className="space-y-3">
                        <div className="flex items-center gap-2 text-emerald-800 font-extrabold text-sm uppercase tracking-wide">
                          <CheckCircle className="h-4.5 w-4.5 text-emerald-500" />
                          Key Strengths
                        </div>
                        <ul className="space-y-2.5">
                          {result.strengths.map((str, i) => (
                            <li key={i} className="flex gap-2 text-xs text-slate-700">
                              <span className="text-emerald-500 font-extrabold shrink-5">✓</span>
                              <span className="font-semibold">{str}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                      {/* Improvement opportunities */}
                      <div className="space-y-3">
                        <div className="flex items-center gap-2 text-indigo-950 font-extrabold text-sm uppercase tracking-wide">
                          <ArrowRight className="h-4.5 w-4.5 text-indigo-500" />
                          ATS Fixes Required
                        </div>
                        <ul className="space-y-2.5">
                          {result.improvements.map((imp, i) => (
                            <li key={i} className="flex gap-2 text-xs text-slate-700">
                              <span className="text-indigo-500 shrink-0 font-extrabold">▶</span>
                              <span className="font-semibold">{imp}</span>
                            </li>
                          ))}
                        </ul>
                      </div>

                    </div>

                  </div>

                  {/* DETAILED ADVICE & FORMATTING (MARKDOWN WRAPPER) */}
                  <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                    <div className="flex items-center gap-2 mb-4 pb-3 border-b border-slate-100 uppercase tracking-widest text-xs font-black text-slate-500">
                      <BookOpen className="h-4.5 w-4.5 text-indigo-600" />
                      Detailed Optimization Actions
                    </div>
                    
                    <div className="markdown-body prose max-w-none text-sm text-slate-700 leading-relaxed font-sans space-y-4">
                      <Markdown>{result.detailed_analysis}</Markdown>
                    </div>
                  </div>

                </motion.div>
              )}

            </AnimatePresence>

          </div>

        </div>
      </main>

      <footer className="border-t border-slate-200 bg-white mt-20">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 text-center text-xs font-semibold text-slate-400 font-mono">
          <p>AI Resume Analyzer Compliance Core | Developed with @google/genai & Streamlit matching standards</p>
        </div>
      </footer>
    </div>
  );
}
