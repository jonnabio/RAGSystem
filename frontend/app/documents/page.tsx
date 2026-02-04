"use client";

import { FileText, Search, Upload } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { trackActivity } from "../lib/analytics";

interface Document {
  id: string;
  filename: string;
  status: string;
  chunk_count: number;
  size_bytes: number;
  document_type: string;
  uploaded_at: string;
}

type FilterTab = "all" | "pdfs" | "word" | "recent";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const [activeTab, setActiveTab] = useState<FilterTab>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [currentTime, setCurrentTime] = useState(Date.now());

  const fetchDocuments = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/documents`,
      );
      if (response.ok) {
        const data = await response.json();
        setDocuments(data);
      }
    } catch (error) {
      console.error("Error fetching documents:", error);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  useEffect(() => {
    setCurrentTime(Date.now());
  }, [documents, activeTab]);

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    setUploadProgress(0);

    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) return prev;
        return prev + 10;
      });
    }, 500);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/documents/upload`,
        {
          method: "POST",
          body: formData,
        },
      );

      clearInterval(interval);

      if (response.ok) {
        setUploadProgress(100);

        // Track as activity
        trackActivity({
          type: "upload",
          title: `Uploaded: "${file.name}"`,
          description: `${(file.size / 1024).toFixed(1)} KB`,
          timestamp: new Date(),
        });

        await fetchDocuments();
        setTimeout(() => {
          setIsUploading(false);
          setUploadProgress(0);
        }, 500);
      } else {
        const errorText = await response.text();
        alert(`Upload failed: ${errorText}`);
        setIsUploading(false);
        setUploadProgress(0);
      }
    } catch (error) {
      clearInterval(interval);
      console.error("Upload error:", error);
      alert("Upload failed. Make sure the backend is running.");
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      uploadFile(e.target.files[0]);
    }
  };

  const deleteDocument = async (id: string) => {
    if (!confirm("Are you sure you want to delete this document?")) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/documents/${id}`,
        {
          method: "DELETE",
        },
      );

      if (response.ok) {
        await fetchDocuments();
      }
    } catch (error) {
      console.error("Delete error:", error);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    if (diffDays === 1) return "yesterday";
    return `${diffDays} days ago`;
  };

  // Filter documents
  const dayAgo = currentTime - 86400000;

  const filteredDocuments = documents.filter((doc) => {
    // Search filter
    if (
      searchQuery &&
      !doc.filename.toLowerCase().includes(searchQuery.toLowerCase())
    ) {
      return false;
    }

    // Tab filter
    switch (activeTab) {
      case "pdfs":
        return doc.document_type === "pdf";
      case "word":
        return doc.document_type === "docx" || doc.document_type === "doc";
      case "recent":
        return new Date(doc.uploaded_at).getTime() > dayAgo;
      default:
        return true;
    }
  });

  const tabs: { id: FilterTab; label: string }[] = [
    { id: "all", label: "All" },
    { id: "pdfs", label: "PDFs" },
    { id: "word", label: "Word Docs" },
    { id: "recent", label: "Recently Added" },
  ];

  return (
    <div className="p-8">
      {/* Page Header */}
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">Documents</h1>
        <label htmlFor="file-upload-btn">
          <span className="btn-primary flex items-center gap-2 cursor-pointer px-5 py-2.5">
            <Upload className="w-4 h-4" />
            Upload File
          </span>
        </label>
        <input
          type="file"
          id="file-upload-btn"
          className="hidden"
          accept=".pdf,.docx,.doc"
          onChange={handleFileInput}
          disabled={isUploading}
        />
      </div>

      {/* Upload Dropzone */}
      <div
        className={`mb-8 border-2 border-dashed rounded-xl transition-all duration-300 ${
          dragActive
            ? "border-accent bg-accent/10 scale-[1.02]"
            : "border-white/20 bg-secondary hover:border-white/30"
        } ${isUploading ? "opacity-50 pointer-events-none" : ""}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <label htmlFor="file-upload" className="cursor-pointer block">
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-accent/20 flex items-center justify-center">
              <Upload className="w-8 h-8 text-accent" />
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">
              {isUploading
                ? "Uploading..."
                : "Drag & Drop files here or click to browse"}
            </h3>
            <p className="text-sm text-slate-400">Supported: PDF, DOCX</p>

            {isUploading && (
              <div className="mt-6 max-w-md mx-auto">
                <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-accent to-accent-light h-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-xs text-slate-400 mt-2">
                  Processing... {uploadProgress}%
                </p>
              </div>
            )}
          </div>
        </label>
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept=".pdf,.docx,.doc"
          onChange={handleFileInput}
          disabled={isUploading}
        />
      </div>

      {/* Filter Tabs & Search */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                activeTab === tab.id
                  ? "text-accent border-b-2 border-accent bg-accent/10"
                  : "text-slate-400 hover:text-white hover:bg-white/5"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm
                       text-white placeholder-slate-500 w-64
                       focus:border-accent focus:ring-1 focus:ring-accent
                       transition-all duration-200 outline-none"
          />
        </div>
      </div>

      {/* Documents Grid */}
      {filteredDocuments.length === 0 ? (
        <div className="card text-center py-16">
          <div className="text-5xl mb-4">📂</div>
          <h3 className="text-xl font-semibold text-white mb-2">
            No documents found
          </h3>
          <p className="text-slate-400">
            {searchQuery
              ? "Try adjusting your search"
              : "Upload your first document to get started"}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDocuments.map((doc) => (
            <div
              key={doc.id}
              className="bg-secondary border border-white/5 rounded-xl p-4
                         hover:border-white/10 transition-all duration-200"
            >
              <div className="flex items-start gap-3">
                {/* Icon */}
                <div
                  className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    doc.document_type === "pdf"
                      ? "bg-red-500/20"
                      : "bg-blue-500/20"
                  }`}
                >
                  <FileText
                    className={`w-5 h-5 ${
                      doc.document_type === "pdf"
                        ? "text-red-400"
                        : "text-blue-400"
                    }`}
                  />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <h4 className="text-white font-medium text-sm truncate">
                    {doc.filename}
                  </h4>
                  <p className="text-slate-400 text-xs mt-1">
                    {formatFileSize(doc.size_bytes)} • {doc.chunk_count} chunks
                    • {formatDate(doc.uploaded_at)}
                  </p>

                  {/* Status */}
                  <div className="mt-2">
                    {doc.status === "completed" && (
                      <span className="badge-success text-xs">✓ Processed</span>
                    )}
                    {doc.status === "processing" && (
                      <span className="badge-warning text-xs animate-pulse">
                        ⏳ Processing...
                      </span>
                    )}
                    {doc.status === "failed" && (
                      <span className="badge-error text-xs">✗ Failed</span>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="mt-3 flex gap-2">
                    <button className="text-xs px-3 py-1.5 bg-blue-600/20 text-blue-400 rounded-lg hover:bg-blue-600/30 transition-colors">
                      View
                    </button>
                    <Link href={`/chat?doc=${doc.id}`}>
                      <button className="text-xs px-3 py-1.5 bg-accent/20 text-accent rounded-lg hover:bg-accent/30 transition-colors">
                        Use in Chat
                      </button>
                    </Link>
                    <button
                      onClick={() => deleteDocument(doc.id)}
                      className="text-xs px-3 py-1.5 border border-white/10 text-slate-400 rounded-lg
                                 hover:border-red-500/50 hover:text-red-400 transition-colors"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
