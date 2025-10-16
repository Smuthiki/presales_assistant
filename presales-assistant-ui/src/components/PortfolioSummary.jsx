import React, { useState } from "react";
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Chip,
  IconButton,
  CircularProgress,
  Link,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ExpandLessIcon from "@mui/icons-material/ExpandLess";
import SearchIcon from "@mui/icons-material/Search";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import DownloadIcon from "@mui/icons-material/Download";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import InfoIcon from "@mui/icons-material/Info";
import SummarizeIcon from "@mui/icons-material/Summarize";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
// eslint-disable-next-line no-unused-vars
import BusinessIcon from "@mui/icons-material/Business";
import DevicesIcon from "@mui/icons-material/Devices";
import AnnouncementIcon from "@mui/icons-material/Announcement";
import PartnershipIcon from "@mui/icons-material/Handshake";
import LaunchIcon from "@mui/icons-material/Launch";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import TargetIcon from "@mui/icons-material/GpsFixed";
import ReactMarkdown from "react-markdown";
import { getPortfolioSummary, getPortfolioSummarySelected, determineIndustry } from "../api";
import Loader from "./Loader";
import axios from "axios";

export default function PortfolioSummaryEnhanced({ customer, detectedIndustry }) {
  const [localCustomer, setLocalCustomer] = useState(customer || "");

  const [industry, setIndustry] = useState(detectedIndustry || "");
  const [industryConfidence, setIndustryConfidence] = useState(null);
  const [detectingIndustry, setDetectingIndustry] = useState(false);
  const [technology, setTechnology] = useState("");
  const [focus, setFocus] = useState("");

  const [companyWebsite, setCompanyWebsite] = useState("");
  const [limit, setLimit] = useState(6);
  const [matchedRows, setMatchedRows] = useState([]);
  const [selectedRowIndices, setSelectedRowIndices] = useState([]);
  const [intelligenceData, setIntelligenceData] = useState(null);
  const [shortPitch, setShortPitch] = useState("");
  const [longPitch, setLongPitch] = useState("");
  const [longPitchStructured, setLongPitchStructured] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pitchGenerated, setPitchGenerated] = useState(false);
  const [expandedRowIndex, setExpandedRowIndex] = useState(null);
  const [refining, setRefining] = useState(false);
  const [refinementInstructions, setRefinementInstructions] = useState("");
  const [expandedBulletPoints, setExpandedBulletPoints] = useState(new Set());

  // Industry detection function (separate from portfolio search)
  const handleIndustryDetection = async () => {
    if (!localCustomer.trim()) {
      return;
    }
    
    setDetectingIndustry(true);
    try {
      const response = await determineIndustry(localCustomer);
      console.log("[DEBUG] Industry detection response:", response);
      if (response?.industry && response.industry.trim()) {
        setIndustry(response.industry);
        setIndustryConfidence(response.confidence || 0);
      } else if (response?.data?.industry && response.data.industry.trim()) {
        setIndustry(response.data.industry);
        setIndustryConfidence(response.data.confidence || 0);
      } else {
        setIndustry("Unable to detect");
        setIndustryConfidence(null);
      }
    } catch (error) {
      console.error("Error detecting industry:", error);
      setIndustry("Detection failed");
      setIndustryConfidence(null);
    } finally {
      setDetectingIndustry(false);
    }
  };

  const handleFetchRows = async () => {
    if (!localCustomer.trim()) {
      alert("Please enter a customer name.");
      return;
    }
    setLoading(true);
    setMatchedRows([]);
    setSelectedRowIndices([]);
    setPitchGenerated(false);
    setShortPitch("");
    setLongPitch("");
    setLongPitchStructured(null);
    setExpandedBulletPoints(new Set());
    try {
      const payload = {
        client: localCustomer,
        industry: industry || undefined,
        technology: technology || undefined,
        focus: focus || undefined,

        company_website: companyWebsite || undefined,
        limit: limit,
      };
      console.log("[DEBUG] Fetching rows with payload:", payload);
      const response = await getPortfolioSummary(payload);
      console.log("[DEBUG] Portfolio summary response:", response);
      if (response?.data?.rows && response.data.rows.length > 0) {
        console.log("[DEBUG] Found rows:", response.data.rows.length);
        setMatchedRows(response.data.rows);
        setIntelligenceData(response.data.intelligence_data || null);
        setSelectedRowIndices(response.data.rows.map((_, index) => index));
      } else if (response?.rows && response.rows.length > 0) {
        console.log("[DEBUG] Found rows (direct):", response.rows.length);
        setMatchedRows(response.rows);
        setIntelligenceData(response.intelligence_data || null);
        setSelectedRowIndices(response.rows.map((_, index) => index));
      } else {
        console.log("[DEBUG] No rows found in response");
        setMatchedRows([]);
      }
    } catch (error) {
      console.error("Error fetching portfolio summary:", error);
      console.error("Error response:", error.response);
      alert(`Failed to fetch matching rows: ${error.message}. Check console for details.`);
    } finally {
      setLoading(false);
    }
  };

  const handleBuildPitch = async () => {
    if (selectedRowIndices.length === 0) {
      alert("Please select at least one row to build the pitch.");
      return;
    }
    setLoading(true);
    try {
      const selectedRows = selectedRowIndices.map((index) => matchedRows[index]);
      const payload = {
        client: localCustomer,
        rows: selectedRows,
        intelligence_data: intelligenceData || undefined,
      };
      console.log("[DEBUG] Building pitch with payload:", payload);
      const response = await getPortfolioSummarySelected(payload);
      console.log("[DEBUG] Build pitch response:", response);
      
      if (response?.short_summary && response?.long_summary) {
        console.log("[DEBUG] Found summaries - setting pitch data");
        console.log("[DEBUG] Structured data:", response.long_structured);
        setShortPitch(response.short_summary);
        setLongPitch(response.long_summary);
        setLongPitchStructured(response.long_structured || null);
        setPitchGenerated(true);
        setExpandedBulletPoints(new Set()); // Reset expanded state for new pitch
      } else {
        console.log("[DEBUG] No summaries found in response");
        alert("Failed to generate pitch summary. Please try again.");
      }
    } catch (error) {
      console.error("Error building pitch:", error);
      alert("Failed to build pitch. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAll = () => {
    if (selectedRowIndices.length === matchedRows.length) {
      setSelectedRowIndices([]);
    } else {
      setSelectedRowIndices(matchedRows.map((_, index) => index));
    }
  };

  const toggleRowSelection = (index) => {
    if (selectedRowIndices.includes(index)) {
      setSelectedRowIndices(selectedRowIndices.filter((i) => i !== index));
    } else {
      setSelectedRowIndices([...selectedRowIndices, index]);
    }
  };

  const toggleRowExpansion = (index) => {
    setExpandedRowIndex(expandedRowIndex === index ? null : index);
  };

  const handleDownloadPitch = async () => {
    if (!pitchGenerated) return;
    try {
      const response = await axios.post(
        "http://localhost:8000/download_pitch",
        {
          client: localCustomer,
          short_pitch: shortPitch,
          long_pitch: longPitch,
        },
        { responseType: "blob" }
      );
      const blob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${localCustomer}_pitch.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading pitch:", error);
      alert("Failed to download PDF. Please try again.");
    }
  };

  const handleRefinePitch = async () => {
    if (!pitchGenerated || !refinementInstructions.trim()) return;
    setRefining(true);
    try {
      const selectedRows = selectedRowIndices.map((index) => matchedRows[index]);
      const payload = {
        client: localCustomer,
        current_short_pitch: shortPitch,
        current_long_pitch: longPitch,
        refinement_instructions: refinementInstructions,
        context_rows: selectedRows,
        intelligence_data: intelligenceData || undefined,
      };
      const response = await axios.post("http://localhost:8000/refine_pitch", payload);
      if (response.data?.short_pitch && response.data?.long_pitch) {
        setShortPitch(response.data.short_pitch);
        setLongPitch(response.data.long_pitch);
        setRefinementInstructions("");
      } else {
        alert("Failed to refine pitch. Please try again.");
      }
    } catch (error) {
      console.error("Error refining pitch:", error);
      alert("Failed to refine pitch. Please try again.");
    } finally {
      setRefining(false);
    }
  };

  const renderMatchedRow = (row, index) => {
    const isSelected = selectedRowIndices.includes(index);
    const isExpanded = expandedRowIndex === index;

    // Helper function to get project status color
    const getStatusColor = (status) => {
      if (!status) return "#9e9e9e";
      const statusLower = status.toLowerCase();
      if (statusLower.includes("active") || statusLower.includes("ongoing")) return "#4caf50";
      if (statusLower.includes("completed") || statusLower.includes("closed")) return "#2196f3";
      if (statusLower.includes("pending") || statusLower.includes("review")) return "#ff9800";
      return "#9e9e9e";
    };

    return (
      <Card
        key={index}
        onClick={() => toggleRowSelection(index)}
        sx={{
          mb: 2,
          cursor: "pointer",
          border: isSelected ? "3px solid #1976d2" : "2px solid #e3f2fd",
          bgcolor: isSelected ? "#f3f8ff" : "white",
          borderRadius: 3,
          transition: "all 0.3s ease-in-out",
          "&:hover": { 
            boxShadow: 6,
            transform: "translateY(-2px)",
            borderColor: isSelected ? "#1976d2" : "#90caf9"
          },
          minHeight: "200px",
          maxHeight: isExpanded ? "500px" : "220px",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          position: "relative"
        }}
      >
        {/* Header Section */}
        <Box sx={{ 
          bgcolor: isSelected ? "#1976d2" : "#e3f2fd", 
          p: 2, 
          borderRadius: "12px 12px 0 0",
          position: "relative"
        }}>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" sx={{ 
                fontWeight: 700, 
                color: isSelected ? "white" : "#1976d2",
                fontSize: "1.1rem",
                mb: 0.5
              }}>
                🏢 {row.client_name || "Unknown Client"}
              </Typography>
              <Box sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap" }}>
                {row.match_score && (
                  <Chip
                    label={`${row.match_score}% Match`}
                    size="small"
                    sx={{ 
                      bgcolor: isSelected ? "rgba(255,255,255,0.2)" : "#4caf50",
                      color: isSelected ? "white" : "white",
                      fontWeight: 600,
                      fontSize: "0.75rem"
                    }}
                  />
                )}
                {row.status && (
                  <Chip
                    label={row.status}
                    size="small"
                    sx={{ 
                      bgcolor: getStatusColor(row.status),
                      color: "white",
                      fontSize: "0.7rem",
                      fontWeight: 500
                    }}
                  />
                )}
                {row.industry && (
                  <Chip
                    label={row.industry}
                    size="small"
                    variant="outlined"
                    sx={{ 
                      borderColor: isSelected ? "rgba(255,255,255,0.5)" : "#1976d2",
                      color: isSelected ? "white" : "#1976d2",
                      fontSize: "0.7rem"
                    }}
                  />
                )}
              </Box>
            </Box>
            
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              {isSelected && <CheckCircleIcon sx={{ color: "white", fontSize: 24 }} />}
              <IconButton
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleRowExpansion(index);
                }}
                sx={{ 
                  color: isSelected ? "white" : "#1976d2",
                  bgcolor: isSelected ? "rgba(255,255,255,0.1)" : "rgba(25,118,210,0.1)",
                  "&:hover": {
                    bgcolor: isSelected ? "rgba(255,255,255,0.2)" : "rgba(25,118,210,0.2)"
                  }
                }}
              >
                {isExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>
          </Box>
        </Box>

        <CardContent sx={{ p: 2, flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          {/* Quick Overview Section */}
          <Box sx={{ mb: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Box sx={{ p: 1.5, bgcolor: "#f8f9fa", borderRadius: 2, border: "1px solid #e0e0e0" }}>
                  <Typography variant="caption" sx={{ fontWeight: 600, color: "#666", textTransform: "uppercase" }}>
                    💻 Technologies
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 0.5, fontWeight: 500 }}>
                    {row.technologies || "Not specified"}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={6}>
                <Box sx={{ p: 1.5, bgcolor: "#e8f5e8", borderRadius: 2, border: "1px solid #4caf50" }}>
                  <Typography variant="caption" sx={{ fontWeight: 600, color: "#2e7d32", textTransform: "uppercase" }}>
                    🎯 Practice Area
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 0.5, fontWeight: 500 }}>
                    {row.practice || "General Practice"}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Box>

          {/* Expandable Details Section */}
          {isExpanded && (
            <Box sx={{ 
              flex: 1,
              overflowY: "auto",
              "&::-webkit-scrollbar": { width: "6px" },
              "&::-webkit-scrollbar-track": { bgcolor: "#f1f1f1", borderRadius: "3px" },
              "&::-webkit-scrollbar-thumb": { bgcolor: "#4caf50", borderRadius: "3px" },
              "&::-webkit-scrollbar-thumb:hover": { bgcolor: "#388e3c" }
            }}>
              {/* Problem & Opportunity */}
              {row.problem_or_opportunity_statement && (
                <Box sx={{ mb: 2, p: 2, bgcolor: "#fff3e0", borderRadius: 2, border: "1px solid #ff9800" }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#f57c00", mb: 1, display: "flex", alignItems: "center" }}>
                    🎯 Problem / Opportunity Statement
                  </Typography>
                  <Typography variant="body2" sx={{ lineHeight: 1.5 }}>
                    {row.problem_or_opportunity_statement}
                  </Typography>
                </Box>
              )}

              {/* Business Case */}
              {row.business_case && (
                <Box sx={{ mb: 2, p: 2, bgcolor: "#e3f2fd", borderRadius: 2, border: "1px solid #2196f3" }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#1976d2", mb: 1, display: "flex", alignItems: "center" }}>
                    💼 Business Case
                  </Typography>
                  <Typography variant="body2" sx={{ lineHeight: 1.5 }}>
                    {row.business_case}
                  </Typography>
                </Box>
              )}

              {/* Evoke Solution */}
              {row["evoke_solution_/_value_add_to_the_customer_(what_/_how)"] && (
                <Box sx={{ mb: 2, p: 2, bgcolor: "#e8f5e8", borderRadius: 2, border: "1px solid #4caf50" }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#2e7d32", mb: 1, display: "flex", alignItems: "center" }}>
                    🚀 Evoke Solution & Value Add
                  </Typography>
                  <Typography variant="body2" sx={{ lineHeight: 1.5 }}>
                    {row["evoke_solution_/_value_add_to_the_customer_(what_/_how)"]}
                  </Typography>
                </Box>
              )}

              {/* Evoke Role */}
              {row.evoke_role && (
                <Box sx={{ mb: 2, p: 2, bgcolor: "#f3e5f5", borderRadius: 2, border: "1px solid #9c27b0" }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#7b1fa2", mb: 1, display: "flex", alignItems: "center" }}>
                    👥 Evoke Role & Deliverables
                  </Typography>
                  <Typography variant="body2" sx={{ lineHeight: 1.5 }}>
                    {row.evoke_role}
                  </Typography>
                </Box>
              )}

              {/* Key Deliverables */}
              {row.key_deliverables && (
                <Box sx={{ mb: 2, p: 2, bgcolor: "#fff8e1", borderRadius: 2, border: "1px solid #ffc107" }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#f57c00", mb: 1, display: "flex", alignItems: "center" }}>
                    📋 Key Deliverables
                  </Typography>
                  <Typography variant="body2" sx={{ lineHeight: 1.5 }}>
                    {row.key_deliverables}
                  </Typography>
                </Box>
              )}

              {/* Match Reasoning */}
              {row.detailed_reasoning && (
                <Box sx={{ mt: 2, p: 2, bgcolor: "#f5f5f5", borderRadius: 2, border: "2px solid #9e9e9e" }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#424242", mb: 1, display: "flex", alignItems: "center" }}>
                    🧠 AI Match Reasoning
                  </Typography>
                  <Box sx={{ 
                    bgcolor: "white", 
                    p: 1.5, 
                    borderRadius: 1, 
                    border: "1px solid #e0e0e0",
                    fontFamily: "monospace",
                    fontSize: "0.85rem"
                  }}>
                    <Typography variant="body2" sx={{ whiteSpace: "pre-line", lineHeight: 1.4 }}>
                      {row.detailed_reasoning}
                    </Typography>
                  </Box>
                </Box>
              )}
            </Box>
          )}


        </CardContent>
      </Card>
    );
  };

  // Helper function to parse long pitch into structured sections with intelligent bullet points
  const parseLongPitchIntoSections = (longPitchText, structuredData = null) => {
    // First, try to use structured data from backend if available
    if (structuredData && structuredData.sections && Array.isArray(structuredData.sections)) {
      console.log('[DEBUG] Using structured data from backend', structuredData);
      return structuredData.sections.map(section => ({
        title: section.title,
        bulletPoints: section.bullet_points || section.bulletPoints || []
      }));
    }

    // Fallback to text parsing if no structured data
    if (!longPitchText) return [];

    const sections = [];
    
    // Enhanced section headers to identify
    const sectionHeaders = [
      'Business Context',
      'Evoke\'s Experience', 
      'Evoke\'s Relevant Experience',
      'Strategic Fit', 
      'Value Proposition',
      'Strategic Fit & Value Proposition',
      'Competitive Advantage',
      'Implementation Approach',
      'Technical Expertise',
      'Industry Experience',
      'Relevant Experience',
      'Why Evoke',
      'Our Approach',
      'Next Steps & Engagement Model',
      'Next Steps'
    ];

    // Split content into sections first
    const lines = longPitchText.split('\n').map(line => line.trim()).filter(line => line);
    let currentSection = null;
    let sectionContent = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      // Check if this line is a section header
      const isHeader = sectionHeaders.some(header => 
        line.toLowerCase().includes(header.toLowerCase()) ||
        line.match(/^#+\s/) || // Markdown headers
        line.match(/^\*\*.*\*\*$/) || // Bold text
        (line.length < 80 && line.includes(':') && !line.includes('•') && !line.includes('-') && !line.includes('.'))
      );

      if (isHeader) {
        // Process previous section
        if (currentSection && sectionContent.length > 0) {
          const bulletPoints = createIntelligentBulletPoints(sectionContent.join(' '));
          sections.push({
            title: currentSection,
            bulletPoints: bulletPoints
          });
        }

        // Start new section
        currentSection = line.replace(/^#+\s*/, '').replace(/\*\*/g, '').replace(/:$/, '').trim();
        sectionContent = [];
      } else {
        // Add content to current section
        if (currentSection) {
          sectionContent.push(line);
        }
      }
    }

    // Process final section
    if (currentSection && sectionContent.length > 0) {
      const bulletPoints = createIntelligentBulletPoints(sectionContent.join(' '));
      sections.push({
        title: currentSection,
        bulletPoints: bulletPoints
      });
    }

    // If no structured sections found, create default sections
    if (sections.length === 0 && longPitchText) {
      const bulletPoints = createIntelligentBulletPoints(longPitchText);
      sections.push({
        title: 'Pitch Summary',
        bulletPoints: bulletPoints
      });
    }

    return sections;
  };

  // Helper function to create intelligent bullet points from text content
  const createIntelligentBulletPoints = (content) => {
    if (!content || content.trim().length === 0) return [];

    // Split content into sentences
    const sentences = content.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 20);
    
    if (sentences.length === 0) return [];

    // Group sentences into logical bullet points (2-3 sentences each)
    const bulletPoints = [];
    const sentencesPerBullet = Math.max(1, Math.floor(sentences.length / Math.max(1, Math.ceil(sentences.length / 3))));
    
    for (let i = 0; i < sentences.length; i += sentencesPerBullet) {
      const bulletSentences = sentences.slice(i, i + sentencesPerBullet);
      const fullText = bulletSentences.join('. ').trim() + '.';
      
      // Extract key themes for the summary
      const keyWords = extractKeyThemes(fullText);
      let summary = '';
      
      if (keyWords.length > 0) {
        // Create a meaningful summary from key themes
        summary = `${keyWords.slice(0, 3).join(', ')} - ${bulletSentences[0].substring(0, 80)}${bulletSentences[0].length > 80 ? '...' : ''}`;
      } else {
        // Fallback to first sentence summary
        summary = bulletSentences[0].substring(0, 120) + (bulletSentences[0].length > 120 ? '...' : '');
      }

      bulletPoints.push({
        summary: summary,
        details: [fullText]
      });
    }

    return bulletPoints;
  };

  // Helper function to extract key themes from text
  const extractKeyThemes = (text) => {
    if (!text) return [];
    
    // Key business and technical terms to look for
    const keyTerms = [
      'growth', 'revenue', 'market', 'strategic', 'digital transformation', 'technology', 
      'AI', 'IoT', 'cloud', 'efficiency', 'competitive', 'innovation', 'experience',
      'expertise', 'solutions', 'services', 'partnership', 'value', 'ROI', 'transformation',
      'automation', 'analytics', 'integration', 'scalability', 'security', 'compliance'
    ];

    const lowerText = text.toLowerCase();
    const foundTerms = keyTerms.filter(term => lowerText.includes(term.toLowerCase()));
    
    return foundTerms.slice(0, 5); // Return top 5 relevant terms
  };

  // Toggle bullet point expansion
  const toggleBulletPoint = (sectionIndex, bulletIndex) => {
    const bulletId = `${sectionIndex}-${bulletIndex}`;
    const newExpanded = new Set(expandedBulletPoints);
    
    if (newExpanded.has(bulletId)) {
      newExpanded.delete(bulletId);
    } else {
      newExpanded.add(bulletId);
    }
    
    setExpandedBulletPoints(newExpanded);
  };

  // Render interactive bullet point
  const renderBulletPoint = (bulletPoint, sectionIndex, bulletIndex) => {
    const bulletId = `${sectionIndex}-${bulletIndex}`;
    const isExpanded = expandedBulletPoints.has(bulletId);

    return (
      <Box 
        key={bulletIndex}
        sx={{ 
          mb: 1.5,
          border: "1px solid #e0e0e0",
          borderRadius: 2,
          overflow: "hidden",
          transition: "all 0.2s ease-in-out",
          "&:hover": { borderColor: "#1976d2", boxShadow: 1 }
        }}
      >
        {/* Clickable Summary */}
        <Box
          onClick={() => toggleBulletPoint(sectionIndex, bulletIndex)}
          sx={{
            p: 1.5,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            bgcolor: isExpanded ? "#f0f7ff" : "#fafafa",
            borderBottom: isExpanded ? "1px solid #e0e0e0" : "none",
            "&:hover": { bgcolor: isExpanded ? "#e3f2fd" : "#f0f0f0" }
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", flex: 1 }}>
            <Box
              sx={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                bgcolor: "#1976d2",
                mr: 1.5,
                flexShrink: 0
              }}
            />
            <Typography 
              variant="body2" 
              sx={{ 
                fontWeight: 500, 
                color: "#2c2c2c",
                lineHeight: 1.4
              }}
            >
              {bulletPoint.summary}
            </Typography>
          </Box>
          {bulletPoint.details.length > 0 && (
            <Box sx={{ ml: 1, flexShrink: 0 }}>
              {isExpanded ? (
                <ExpandLessIcon sx={{ color: "#1976d2", fontSize: 20 }} />
              ) : (
                <ExpandMoreIcon sx={{ color: "#666", fontSize: 20 }} />
              )}
            </Box>
          )}
        </Box>

        {/* Expandable Details */}
        {isExpanded && bulletPoint.details.length > 0 && (
          <Box
            sx={{
              p: 2,
              bgcolor: "#f8f9fa",
              borderTop: "1px solid #e0e0e0"
            }}
          >
            {bulletPoint.details.map((detail, detailIndex) => (
              <Typography
                key={detailIndex}
                variant="body2"
                sx={{
                  color: "#555",
                  lineHeight: 1.6,
                  mb: detailIndex < bulletPoint.details.length - 1 ? 1 : 0
                }}
              >
                {detail}
              </Typography>
            ))}
          </Box>
        )}
      </Box>
    );
  };

  const renderPitchSummaryContent = () => {
    if (!pitchGenerated) {
      return (
        <Box sx={{ 
          display: "flex", 
          flexDirection: "column", 
          alignItems: "center", 
          justifyContent: "center", 
          height: "100%", 
          color: "#666" 
        }}>
          <InfoIcon sx={{ fontSize: 48, mb: 2, color: "#ccc" }} />
          <Typography variant="h6" sx={{ mb: 1, fontWeight: 500 }}>
            No Pitch Generated Yet
          </Typography>
          <Typography variant="body2" sx={{ textAlign: "center" }}>
            Select rows from the left panel and click "Build Pitch" to generate your summary.
          </Typography>
        </Box>
      );
    }

    return (
      <Box sx={{ 
        height: "100%", 
        display: "flex", 
        flexDirection: "column",
        overflow: "visible" // Changed from hidden to visible
      }}>
        {shortPitch && (
          <Box sx={{ mb: 3, flexShrink: 0, minHeight: "auto" }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: "#1976d2", flexShrink: 0 }}>
              📄 Short Summary
            </Typography>
            <Box sx={{ 
              p: 2, 
              bgcolor: "#f8f9fa", 
              borderRadius: 2,
              height: "160px", // Slightly reduced height to ensure visibility
              overflowY: "auto",
              flexShrink: 0, // Prevent shrinking
              "&::-webkit-scrollbar": { 
                width: "8px",
                height: "8px"
              },
              "&::-webkit-scrollbar-track": { 
                bgcolor: "#f1f1f1", 
                borderRadius: "10px" 
              },
              "&::-webkit-scrollbar-thumb": { 
                bgcolor: "#888", 
                borderRadius: "10px",
                border: "1px solid #f1f1f1"
              },
              "&::-webkit-scrollbar-thumb:hover": { 
                bgcolor: "#555" 
              }
            }}>
              <ReactMarkdown>{shortPitch}</ReactMarkdown>
            </Box>
          </Box>
        )}

        {longPitch && (
          <Box sx={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0, mb: 6 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: "#1976d2", flexShrink: 0 }}>
              📋 Interactive Pitch Summary
            </Typography>
            <Box sx={{ 
              flex: 1,
              overflowY: "auto",
              minHeight: "200px", // Ensure minimum height
              maxHeight: shortPitch ? "320px" : "400px", // Increased dynamic height for better content visibility
              pb: 4, // Add bottom padding inside the scrollable area
              "&::-webkit-scrollbar": { 
                width: "8px",
                height: "8px"
              },
              "&::-webkit-scrollbar-track": { 
                bgcolor: "#f1f1f1", 
                borderRadius: "10px" 
              },
              "&::-webkit-scrollbar-thumb": { 
                bgcolor: "#888", 
                borderRadius: "10px",
                border: "1px solid #f1f1f1"
              },
              "&::-webkit-scrollbar-thumb:hover": { 
                bgcolor: "#555" 
              }
            }}>
              {(() => {
                const sections = parseLongPitchIntoSections(longPitch, longPitchStructured);
                
                if (sections.length === 0) {
                  return (
                    <Box sx={{ p: 2, bgcolor: "#f8f9fa", borderRadius: 2 }}>
                      <ReactMarkdown>{longPitch}</ReactMarkdown>
                    </Box>
                  );
                }

                return sections.map((section, sectionIndex) => (
                  <Box key={sectionIndex} sx={{ mb: 3 }}>
                    {/* Section Header */}
                    <Typography 
                      variant="h6" 
                      sx={{ 
                        mb: 2, 
                        fontWeight: 700, 
                        color: "#1976d2",
                        fontSize: "1rem",
                        display: "flex",
                        alignItems: "center",
                        borderLeft: "4px solid #1976d2",
                        pl: 1.5,
                        bgcolor: "#f0f7ff",
                        py: 0.5,
                        borderRadius: "0 8px 8px 0"
                      }}
                    >
                      {section.title}
                      <Chip 
                        label={`${section.bulletPoints.length} points`}
                        size="small" 
                        sx={{ ml: 2, height: 20, fontSize: "0.7rem" }}
                      />
                    </Typography>

                    {/* Bullet Points */}
                    {section.bulletPoints.map((bulletPoint, bulletIndex) => 
                      renderBulletPoint(bulletPoint, sectionIndex, bulletIndex)
                    )}
                  </Box>
                ));
              })()}
            </Box>
          </Box>
        )}
      </Box>
    );
  };

  // Paragraph-style content renderers for AI Intelligence Dashboard
  function renderFinancialContentParagraph() {
    const hasFinancialData = intelligenceData.annual_revenue || intelligenceData.employee_count || intelligenceData.market_position || intelligenceData.industry_focus;
    
    if (!hasFinancialData) {
      return (
        <Typography variant="body2" sx={{ color: "text.secondary", fontStyle: "italic", py: 2 }}>
          No financial or market data available for this company.
        </Typography>
      );
    }

    return (
      <Box>
        {intelligenceData.market_position && (
          <Box sx={{ mb: 1.5, p: 1.5, bgcolor: "#f1f8e9", borderRadius: 2, borderLeft: "4px solid #2e7d32" }}>
            <Typography variant="body2" sx={{ color: "text.primary", lineHeight: 1.5, fontSize: "0.85rem" }}>
              <strong>Market Position:</strong> {typeof intelligenceData.market_position === 'object' ? JSON.stringify(intelligenceData.market_position) : intelligenceData.market_position}
            </Typography>
          </Box>
        )}
        
        {(intelligenceData.annual_revenue || intelligenceData.employee_count) && (
          <Box sx={{ mb: 1.5, p: 1.5, bgcolor: "#e8f5e8", borderRadius: 2 }}>
            {intelligenceData.annual_revenue && (
              <Typography variant="body2" sx={{ color: "text.primary", mb: 0.8, lineHeight: 1.5, fontSize: "0.85rem" }}>
                <strong>Annual Revenue:</strong> {typeof intelligenceData.annual_revenue === 'object' ? JSON.stringify(intelligenceData.annual_revenue) : intelligenceData.annual_revenue}
              </Typography>
            )}
            {intelligenceData.employee_count && (
              <Typography variant="body2" sx={{ color: "text.primary", lineHeight: 1.5, fontSize: "0.85rem" }}>
                <strong>Employee Count:</strong> {typeof intelligenceData.employee_count === 'object' ? JSON.stringify(intelligenceData.employee_count) : intelligenceData.employee_count}
              </Typography>
            )}
          </Box>
        )}

        {intelligenceData.industry_focus && (
          <Box sx={{ p: 1.5, bgcolor: "#f9f9f9", borderRadius: 2 }}>
            <Typography variant="body2" sx={{ color: "text.primary", lineHeight: 1.5, fontSize: "0.85rem" }}>
              <strong>Industry Focus:</strong> {typeof intelligenceData.industry_focus === 'object' ? JSON.stringify(intelligenceData.industry_focus) : intelligenceData.industry_focus}
            </Typography>
          </Box>
        )}
      </Box>
    );
  }

  function renderTechnologyContentParagraph() {
    // Check multiple possible field names for technology data
    const hasTechData = (intelligenceData.technologies && intelligenceData.technologies.length > 0) || 
                       (intelligenceData.tech_confirmed && intelligenceData.tech_confirmed.length > 0) ||
                       (intelligenceData.tech_inferred && intelligenceData.tech_inferred.length > 0) ||
                       intelligenceData.it_infrastructure_summary;
    
    if (!hasTechData) {
      return (
        <Typography variant="body2" sx={{ color: "text.secondary", fontStyle: "italic", py: 2 }}>
          No technology or infrastructure information available.
        </Typography>
      );
    }

    return (
      <Box>
        {/* Render confirmed technologies */}
        {intelligenceData.tech_confirmed && intelligenceData.tech_confirmed.length > 0 && (
          <Box sx={{ mb: 2, p: 2, bgcolor: "#e3f2fd", borderRadius: 2, borderLeft: "4px solid #1976d2" }}>
            <Typography variant="body1" sx={{ color: "text.primary", mb: 1.5, fontWeight: 600 }}>
              ✅ Confirmed Technology Stack:
            </Typography>
            <Typography variant="body1" sx={{ color: "text.primary", lineHeight: 1.6 }}>
              {intelligenceData.tech_confirmed.map(tech => {
                if (typeof tech === 'object' && tech !== null) {
                  return tech.name || tech.technology || tech.theme || JSON.stringify(tech);
                }
                return tech;
              }).join(", ")}
            </Typography>
          </Box>
        )}

        {/* Render legacy technologies format */}
        {intelligenceData.technologies && intelligenceData.technologies.length > 0 && (
          <Box sx={{ mb: 2, p: 2, bgcolor: "#e3f2fd", borderRadius: 2, borderLeft: "4px solid #1976d2" }}>
            <Typography variant="body1" sx={{ color: "text.primary", mb: 1.5, fontWeight: 600 }}>
              Technology Stack & Tools:
            </Typography>
            <Typography variant="body1" sx={{ color: "text.primary", lineHeight: 1.6 }}>
              {intelligenceData.technologies.map(tech => {
                if (typeof tech === 'object' && tech !== null) {
                  return tech.name || tech.technology || JSON.stringify(tech);
                }
                return tech;
              }).join(", ")}
            </Typography>
          </Box>
        )}

        {intelligenceData.it_infrastructure_summary && (
          <Box sx={{ p: 2, bgcolor: "#f0f4ff", borderRadius: 2 }}>
            <Typography variant="body1" sx={{ color: "text.primary", lineHeight: 1.6 }}>
              <strong>IT Infrastructure Overview:</strong> {typeof intelligenceData.it_infrastructure_summary === 'object' ? JSON.stringify(intelligenceData.it_infrastructure_summary) : intelligenceData.it_infrastructure_summary}
            </Typography>
          </Box>
        )}
      </Box>
    );
  }

  function renderVendorsContentParagraph() {
    const hasVendorData = (intelligenceData.vendors && intelligenceData.vendors.length > 0) || 
                         (intelligenceData.partnerships && intelligenceData.partnerships.length > 0) ||
                         (intelligenceData.vendors_confirmed && intelligenceData.vendors_confirmed.length > 0) ||
                         (intelligenceData.vendors_inferred && intelligenceData.vendors_inferred.length > 0);
    
    if (!hasVendorData) {
      return (
        <Typography variant="body2" sx={{ color: "text.secondary", fontStyle: "italic", py: 2 }}>
          No vendor or partnership information available.
        </Typography>
      );
    }

    return (
      <Box>
        {/* Render confirmed vendors */}
        {intelligenceData.vendors_confirmed && intelligenceData.vendors_confirmed.length > 0 && (
          <Box sx={{ mb: 2, p: 2, bgcolor: "#fff3e0", borderRadius: 2, borderLeft: "4px solid #ed6c02" }}>
            <Typography variant="body1" sx={{ color: "text.primary", mb: 1.5, fontWeight: 600 }}>
              ✅ Confirmed Vendors & Technology Partners:
            </Typography>
            <Typography variant="body1" sx={{ color: "text.primary", lineHeight: 1.6 }}>
              The company has confirmed partnerships with {intelligenceData.vendors_confirmed.map(vendor => {
                if (typeof vendor === 'object' && vendor !== null) {
                  return vendor.name || vendor.vendor || vendor.company || vendor.theme || JSON.stringify(vendor);
                }
                return vendor;
              }).join(", ")}. These partnerships indicate their commitment to enterprise-grade solutions.
            </Typography>
          </Box>
        )}

        {/* Render legacy vendors format */}
        {intelligenceData.vendors && intelligenceData.vendors.length > 0 && (
          <Box sx={{ mb: 2, p: 2, bgcolor: "#fff3e0", borderRadius: 2, borderLeft: "4px solid #ed6c02" }}>
            <Typography variant="body1" sx={{ color: "text.primary", mb: 1.5, fontWeight: 600 }}>
              Key Vendors & Technology Partners:
            </Typography>
            <Typography variant="body1" sx={{ color: "text.primary", lineHeight: 1.6 }}>
              The company works with leading technology vendors including {intelligenceData.vendors.map(vendor => {
                if (typeof vendor === 'object' && vendor !== null) {
                  return vendor.name || vendor.vendor || vendor.company || JSON.stringify(vendor);
                }
                return vendor;
              }).join(", ")}. These partnerships indicate their commitment to enterprise-grade solutions and modern technology adoption.
            </Typography>
          </Box>
        )}

        {intelligenceData.partnerships && intelligenceData.partnerships.length > 0 && (
          <Box sx={{ p: 2, bgcolor: "#fef7e0", borderRadius: 2 }}>
            <Typography variant="body1" sx={{ color: "text.primary", mb: 1.5, fontWeight: 600 }}>
              Strategic Partnerships:
            </Typography>
            <Typography variant="body1" sx={{ color: "text.primary", lineHeight: 1.6 }}>
              {intelligenceData.partnerships.map((partnership, index) => (
                <span key={index}>
                  {partnership.partner || 
                   (typeof partnership === 'string' ? partnership : 'Unknown Partner')} - {partnership.type || "Strategic Partner"}
                  {index < intelligenceData.partnerships.length - 1 ? ", " : ""}
                </span>
              ))}
            </Typography>
          </Box>
        )}
      </Box>
    );
  }

  function renderAnnouncementsContentParagraph() {
    const hasAnnouncementData = (intelligenceData.recent_announcements && intelligenceData.recent_announcements.length > 0) ||
                               (intelligenceData.announcements && intelligenceData.announcements.length > 0) ||
                               (intelligenceData.projects && intelligenceData.projects.length > 0);
    
    if (!hasAnnouncementData) {
      return (
        <Typography variant="body2" sx={{ color: "text.secondary", fontStyle: "italic", py: 2 }}>
          No recent announcements or news available.
        </Typography>
      );
    }

    return (
      <Box>
        {/* Render confirmed announcements */}
        {intelligenceData.announcements && intelligenceData.announcements.length > 0 && (
          intelligenceData.announcements.slice(0, 4).map((announcement, index) => (
            <Box key={index} sx={{ 
              mb: 2, 
              p: 2, 
              bgcolor: index % 2 === 0 ? "#ffebee" : "#fce4ec", 
              borderRadius: 2,
              borderLeft: "4px solid #d32f2f"
            }}>
              <Typography variant="body1" sx={{ color: "text.primary", fontWeight: 600, mb: 1 }}>
                📰 {typeof announcement === 'object' ? (announcement.title || announcement.theme || `Update ${index + 1}`) : `Update ${index + 1}`}
              </Typography>
              <Typography variant="body1" sx={{ color: "text.primary", lineHeight: 1.6, mb: 1 }}>
                {typeof announcement === 'object' ? 
                  (announcement.evidence || announcement.description || announcement.summary || 'News update available') :
                  (typeof announcement === 'string' ? announcement : 'News update available')}
              </Typography>
              {typeof announcement === 'object' && announcement.source_url && (
                <Typography variant="caption" sx={{ color: "text.secondary", fontWeight: 500 }}>
                  🔗 Source available
                </Typography>
              )}
            </Box>
          ))
        )}

        {/* Render legacy announcements format */}
        {intelligenceData.recent_announcements && intelligenceData.recent_announcements.slice(0, 4).map((announcement, index) => (
          <Box key={index} sx={{ 
            mb: 2, 
            p: 2, 
            bgcolor: index % 2 === 0 ? "#ffebee" : "#fce4ec", 
            borderRadius: 2,
            borderLeft: "4px solid #d32f2f"
          }}>
            <Typography variant="body1" sx={{ color: "text.primary", fontWeight: 600, mb: 1 }}>
              {announcement.title || `Recent Update ${index + 1}`}
            </Typography>
            <Typography variant="body1" sx={{ color: "text.primary", lineHeight: 1.6, mb: 1 }}>
              {announcement.description || announcement.summary || 
               (typeof announcement === 'string' ? announcement : 'No description available')}
            </Typography>
            {announcement.date && (
              <Typography variant="caption" sx={{ color: "text.secondary", fontWeight: 500 }}>
                📅 {announcement.date}
              </Typography>
            )}
          </Box>
        ))}
      </Box>
    );
  }

  function renderBusinessContextParagraph() {
    const hasBusinessData = intelligenceData.business_context || intelligenceData.strategic_focus || 
                           (intelligenceData.focus_areas && intelligenceData.focus_areas.length > 0);
    
    if (!hasBusinessData) {
      return (
        <Typography variant="body2" sx={{ color: "text.secondary", fontStyle: "italic", py: 2 }}>
          No strategic focus or business context information available.
        </Typography>
      );
    }

    return (
      <Box>
        {intelligenceData.business_context && (
          <Box sx={{ mb: 2, p: 2, bgcolor: "#f3e5f5", borderRadius: 2, borderLeft: "4px solid #7b1fa2" }}>
            <Typography variant="body1" sx={{ color: "text.primary", mb: 1.5, fontWeight: 600 }}>
              Business Context & Overview:
            </Typography>
            <Typography variant="body1" sx={{ color: "text.primary", lineHeight: 1.6 }}>
              {typeof intelligenceData.business_context === 'object' ? JSON.stringify(intelligenceData.business_context) : intelligenceData.business_context}
            </Typography>
          </Box>
        )}

        {intelligenceData.strategic_focus && (
          <Box sx={{ mb: 2, p: 2, bgcolor: "#ede7f6", borderRadius: 2 }}>
            <Typography variant="body1" sx={{ color: "text.primary", mb: 1.5, fontWeight: 600 }}>
              Strategic Focus Areas:
            </Typography>
            <Typography variant="body1" sx={{ color: "text.primary", lineHeight: 1.6 }}>
              {Array.isArray(intelligenceData.strategic_focus) 
                ? intelligenceData.strategic_focus.map((item, index) => (
                    <Box key={index} sx={{ mb: 2, p: 2, bgcolor: "#f8f0ff", borderRadius: 2, borderLeft: "4px solid #7b1fa2" }}>
                      <Typography variant="body1" sx={{ fontWeight: 600, color: "#7b1fa2", mb: 1 }}>
                        🎯 {item.theme || 'Strategic Initiative'}
                      </Typography>
                      <Typography variant="body1" sx={{ color: "text.primary", lineHeight: 1.6, mb: 1 }}>
                        {item.evidence || item.description || 'Strategic focus area identified'}
                      </Typography>
                      {item.priority && (
                        <Typography variant="caption" sx={{ 
                          bgcolor: item.priority === 'high' ? '#ffebee' : item.priority === 'medium' ? '#fff3e0' : '#f3f4f6',
                          color: item.priority === 'high' ? '#d32f2f' : item.priority === 'medium' ? '#f57c00' : '#666',
                          px: 1, py: 0.5, borderRadius: 1, fontWeight: 600, textTransform: 'uppercase'
                        }}>
                          {item.priority} Priority
                        </Typography>
                      )}
                    </Box>
                  ))
                : (typeof intelligenceData.strategic_focus === 'object' ? JSON.stringify(intelligenceData.strategic_focus) : intelligenceData.strategic_focus)}
            </Typography>
          </Box>
        )}

        {intelligenceData.focus_areas && intelligenceData.focus_areas.length > 0 && (
          <Box sx={{ p: 2, bgcolor: "#f1f8ff", borderRadius: 2 }}>
            <Typography variant="body1" sx={{ color: "text.primary", mb: 1.5, fontWeight: 600 }}>
              Key Focus Areas:
            </Typography>
            <Typography variant="body1" sx={{ color: "text.primary", lineHeight: 1.6 }}>
              The company is currently focusing on {intelligenceData.focus_areas.map(area => {
                if (typeof area === 'object' && area !== null) {
                  return area.name || area.area || area.theme || JSON.stringify(area);
                }
                return area;
              }).join(", ")} to drive business growth and maintain competitive advantage in their market segment.
            </Typography>
          </Box>
        )}
      </Box>
    );
  }

  const renderAIIntelligenceDashboard = () => {
    if (!intelligenceData || intelligenceData.error) {
      return null; // Don't show dashboard if no data
    }

    // Debug: Log intelligenceData to see structure
    console.log('Intelligence Data Structure:', intelligenceData);

    // Ultra-compact sub-card component for tight layouts (LEGACY - NOT USED)
    // eslint-disable-next-line no-unused-vars
    const renderSubCard = (title, icon, content, color = "#1976d2", height = "100px") => (
      <Card
        elevation={2}
        sx={{
          height: height,
          border: `1px solid ${color}30`,
          borderLeft: `3px solid ${color}`,
          borderRadius: 1.5,
          mb: 1,
          transition: "all 0.2s ease",
          "&:hover": { 
            boxShadow: 3, 
            borderLeft: `3px solid ${color}`,
            bgcolor: `${color}05`
          },
          display: "flex",
          flexDirection: "column"
        }}
      >
        <CardContent sx={{ p: 1.5, height: "100%", display: "flex", flexDirection: "column" }}>
          <Box sx={{ display: "flex", alignItems: "center", mb: 1, flexShrink: 0 }}>
            {icon}
            <Typography variant="subtitle2" sx={{ ml: 1, fontWeight: 600, color, fontSize: "0.85rem", lineHeight: 1 }}>
              {title}
            </Typography>
          </Box>
          <Box sx={{ 
            flex: 1,
            overflowY: "auto",
            pr: 0.5,
            "&::-webkit-scrollbar": { width: "3px" },
            "&::-webkit-scrollbar-track": { bgcolor: "#f1f1f1", borderRadius: "2px" },
            "&::-webkit-scrollbar-thumb": { bgcolor: `${color}60`, borderRadius: "2px", "&:hover": { bgcolor: `${color}80` } }
          }}>
            {content}
          </Box>
        </CardContent>
      </Card>
    );

    // eslint-disable-next-line no-unused-vars
    const renderFinancialData = () => {
      const financial = intelligenceData.financial_data;
      if (!financial || (!financial.revenue && !financial.market_cap && !financial.growth_rate && 
          !financial.stock_price && !financial.pe_ratio && !financial.dividend_yield && 
          financial.other_metrics?.length === 0)) {
        return (
          <Box sx={{ textAlign: "center", py: 3 }}>
            <Typography variant="body2" color="text.secondary">No financial data available</Typography>
            <Typography variant="caption" sx={{ display: "block", mt: 1, color: "text.disabled" }}>
              Financial data will be automatically fetched when available
            </Typography>
          </Box>
        );
      }

      return (
        <Box>
          {financial.revenue && (
            <Box sx={{ mb: 2, p: 1.5, bgcolor: "#e8f5e8", borderRadius: 1, border: "1px solid #4caf50" }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: "#2e7d32" }}>💰 Revenue</Typography>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>{financial.revenue}</Typography>
              {financial.source_url && (
                <Link href={financial.source_url} target="_blank" sx={{ fontSize: "0.75rem", display: "flex", alignItems: "center", mt: 0.5 }}>
                  <LaunchIcon sx={{ fontSize: 12, mr: 0.5 }} />
                  Verify Source
                </Link>
              )}
            </Box>
          )}
          
          {financial.market_cap && (
            <Box sx={{ mb: 2, p: 1.5, bgcolor: "#f3e5f5", borderRadius: 1, border: "1px solid #9c27b0" }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: "#7b1fa2" }}>📈 Market Cap</Typography>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>{financial.market_cap}</Typography>
            </Box>
          )}

          {financial.stock_price && (
            <Box sx={{ mb: 2, p: 1.5, bgcolor: "#e3f2fd", borderRadius: 1, border: "1px solid #2196f3" }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: "#1976d2" }}>📊 Stock Price</Typography>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>{financial.stock_price}</Typography>
            </Box>
          )}

          {(financial.pe_ratio || financial.dividend_yield || financial.growth_rate) && (
            <Box sx={{ mb: 2, p: 1.5, bgcolor: "#fff3e0", borderRadius: 1, border: "1px solid #ff9800" }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 600, color: "#f57c00", mb: 1 }}>📋 Key Ratios</Typography>
              {financial.pe_ratio && <Typography variant="body2">P/E Ratio: {financial.pe_ratio}</Typography>}
              {financial.dividend_yield && <Typography variant="body2">Dividend Yield: {financial.dividend_yield}</Typography>}
              {financial.growth_rate && <Typography variant="body2">Growth Rate: {financial.growth_rate}</Typography>}
            </Box>
          )}

          {financial.other_metrics?.map((metric, idx) => (
            <Box key={idx} sx={{ mb: 1.5, p: 1, bgcolor: "#fafafa", borderRadius: 1, border: "1px solid #e0e0e0" }}>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                {metric.metric}: {metric.value}
              </Typography>
              {metric.source_url && (
                <Link href={metric.source_url} target="_blank" sx={{ fontSize: "0.75rem", display: "flex", alignItems: "center", mt: 0.5 }}>
                  <LaunchIcon sx={{ fontSize: 12, mr: 0.5 }} />
                  Source
                </Link>
              )}
            </Box>
          ))}
          
          <Box sx={{ mt: 2, p: 1, bgcolor: "#f5f5f5", borderRadius: 1, textAlign: "center" }}>
            <Typography variant="caption" sx={{ color: "text.secondary", fontWeight: 600 }}>
              Data Confidence: {Math.round((financial.confidence || 0) * 100)}%
            </Typography>
          </Box>
        </Box>
      );
    };

    // eslint-disable-next-line no-unused-vars
    const renderTechnologies = () => {
      const tech = intelligenceData.technologies;
      if (!tech || (tech.confirmed?.length === 0 && tech.inferred?.length === 0)) {
        return (
          <Box sx={{ textAlign: "center", py: 3 }}>
            <Typography variant="body2" color="text.secondary">No technology data available</Typography>
            <Typography variant="caption" sx={{ display: "block", mt: 1, color: "text.disabled" }}>
              Enhance search queries for better tech stack discovery
            </Typography>
          </Box>
        );
      }

      return (
        <Box>
          {tech.confirmed?.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#2e7d32", mb: 1.5, display: "flex", alignItems: "center" }}>
                <CheckCircleIcon sx={{ fontSize: 16, mr: 0.5 }} />
                Confirmed Technologies
              </Typography>
              {tech.confirmed.slice(0, 6).map((item, idx) => (
                <Box key={idx} sx={{ mb: 1.5, p: 1.5, bgcolor: "#e8f5e8", borderRadius: 1, border: "1px solid #4caf50" }}>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 0.5 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>{item.name}</Typography>
                    {item.category && (
                      <Chip label={item.category} size="small" sx={{ ml: 1, height: 20, fontSize: "0.7rem" }} />
                    )}
                  </Box>
                  {item.source_url && (
                    <Link href={item.source_url} target="_blank" sx={{ fontSize: "0.75rem", display: "flex", alignItems: "center" }}>
                      <LaunchIcon sx={{ fontSize: 12, mr: 0.5 }} />
                      Verify Source
                    </Link>
                  )}
                </Box>
              ))}
              {tech.confirmed.length > 6 && (
                <Typography variant="caption" color="text.secondary">
                  +{tech.confirmed.length - 6} more technologies found
                </Typography>
              )}
            </Box>
          )}
          
          {tech.inferred?.length > 0 && (
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#ed6c02", mb: 1.5, display: "flex", alignItems: "center" }}>
                <InfoIcon sx={{ fontSize: 16, mr: 0.5 }} />
                Inferred Technologies
              </Typography>
              {tech.inferred.slice(0, 4).map((item, idx) => (
                <Box key={idx} sx={{ mb: 1.5, p: 1.5, bgcolor: "#fff3e0", borderRadius: 1, border: "1px solid #ff9800" }}>
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>{item.name}</Typography>
                  <Typography variant="caption" sx={{ color: "text.secondary", fontStyle: "italic" }}>
                    {item.reason}
                  </Typography>
                </Box>
              ))}
            </Box>
          )}
        </Box>
      );
    };

    // eslint-disable-next-line no-unused-vars
    const renderVendorsPartners = () => {
      const vendors = intelligenceData.vendors_partners;
      if (!vendors || (vendors.confirmed?.length === 0 && vendors.inferred?.length === 0)) {
        return (
          <Box sx={{ textAlign: "center", py: 3 }}>
            <Typography variant="body2" color="text.secondary">No vendor/partner data available</Typography>
            <Typography variant="caption" sx={{ display: "block", mt: 1, color: "text.disabled" }}>
              Try more specific partnership-focused search queries
            </Typography>
          </Box>
        );
      }

      return (
        <Box>
          {vendors.confirmed?.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#2e7d32", mb: 1.5, display: "flex", alignItems: "center" }}>
                <CheckCircleIcon sx={{ fontSize: 16, mr: 0.5 }} />
                Confirmed Partners
              </Typography>
              {vendors.confirmed.slice(0, 5).map((item, idx) => (
                <Box key={idx} sx={{ mb: 1.5, p: 1.5, bgcolor: "#e8f5e8", borderRadius: 1, border: "1px solid #4caf50" }}>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 0.5 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>{item.name}</Typography>
                    {item.relationship_type && (
                      <Chip label={item.relationship_type} size="small" color="primary" sx={{ ml: 1, height: 20, fontSize: "0.7rem" }} />
                    )}
                  </Box>
                  {item.source_url && (
                    <Link href={item.source_url} target="_blank" sx={{ fontSize: "0.75rem", display: "flex", alignItems: "center" }}>
                      <LaunchIcon sx={{ fontSize: 12, mr: 0.5 }} />
                      View Partnership
                    </Link>
                  )}
                </Box>
              ))}
            </Box>
          )}
          
          {vendors.inferred?.length > 0 && (
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#ed6c02", mb: 1.5, display: "flex", alignItems: "center" }}>
                <InfoIcon sx={{ fontSize: 16, mr: 0.5 }} />
                Potential Partners
              </Typography>
              {vendors.inferred.slice(0, 4).map((item, idx) => (
                <Box key={idx} sx={{ mb: 1.5, p: 1.5, bgcolor: "#fff3e0", borderRadius: 1, border: "1px solid #ff9800" }}>
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>{item.name}</Typography>
                  <Typography variant="caption" sx={{ color: "text.secondary", fontStyle: "italic" }}>
                    {item.reason}
                  </Typography>
                </Box>
              ))}
            </Box>
          )}
        </Box>
      );
    };

    // eslint-disable-next-line no-unused-vars
    const renderAnnouncements = () => {
      const announcements = intelligenceData.announcements;
      if (!announcements || announcements.length === 0) {
        return (
          <Box sx={{ textAlign: "center", py: 3 }}>
            <Typography variant="body2" color="text.secondary">No recent announcements available</Typography>
            <Typography variant="caption" sx={{ display: "block", mt: 1, color: "text.disabled" }}>
              Check press release sites and news sources
            </Typography>
          </Box>
        );
      }

      return (
        <Box>
          {announcements.slice(0, 4).map((item, idx) => (
            <Box key={idx} sx={{ mb: 2.5, p: 2, bgcolor: "#fafafa", borderRadius: 2, border: "1px solid #e0e0e0", 
              "&:hover": { bgcolor: "#f5f5f5", boxShadow: 2 } }}>
              <Typography variant="body2" sx={{ fontWeight: 700, mb: 1, color: "#d32f2f" }}>
                📢 {item.title}
              </Typography>
              <Typography variant="body2" sx={{ mb: 1.5, color: "text.primary", lineHeight: 1.5 }}>
                {item.summary}
              </Typography>
              <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                {item.date && (
                  <Typography variant="caption" sx={{ color: "text.secondary", fontWeight: 500 }}>
                    📅 {item.date}
                  </Typography>
                )}
                {item.source_url && (
                  <Link href={item.source_url} target="_blank" sx={{ fontSize: "0.75rem", display: "flex", alignItems: "center" }}>
                    <LaunchIcon sx={{ fontSize: 12, mr: 0.5 }} />
                    Read Full Article
                  </Link>
                )}
              </Box>
              {item.impact && (
                <Box sx={{ mt: 1, p: 1, bgcolor: "#e3f2fd", borderRadius: 1 }}>
                  <Typography variant="caption" sx={{ color: "#1976d2", fontWeight: 600 }}>
                    💼 Impact: {item.impact}
                  </Typography>
                </Box>
              )}
            </Box>
          ))}
          {announcements.length > 4 && (
            <Typography variant="caption" color="text.secondary" sx={{ textAlign: "center", display: "block" }}>
              +{announcements.length - 4} more announcements found
            </Typography>
          )}
        </Box>
      );
    };

    // eslint-disable-next-line no-unused-vars
    const renderStrategicFocus = () => {
      const strategic = intelligenceData.strategic_focus;
      if (!strategic || strategic.length === 0) {
        return (
          <Box sx={{ textAlign: "center", py: 3 }}>
            <Typography variant="body2" color="text.secondary">No strategic focus data available</Typography>
            <Typography variant="caption" sx={{ display: "block", mt: 1, color: "text.disabled" }}>
              Add focus area to search queries for better results
            </Typography>
          </Box>
        );
      }

      return (
        <Box>
          {strategic.slice(0, 5).map((item, idx) => (
            <Box key={idx} sx={{ mb: 2.5, p: 2, bgcolor: "#f3f8ff", borderRadius: 2, border: "1px solid #7b1fa2",
              "&:hover": { bgcolor: "#f0f4ff", boxShadow: 2 } }}>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 700, color: "#7b1fa2" }}>
                  🎯 {typeof item.theme === 'object' ? (item.theme.name || item.theme.title || 'Focus Area') : item.theme}
                </Typography>
                {item.priority && (
                  <Chip 
                    label={item.priority} 
                    size="small" 
                    color={item.priority === 'high' ? 'error' : item.priority === 'medium' ? 'warning' : 'default'}
                    sx={{ ml: 1, height: 20, fontSize: "0.7rem" }}
                  />
                )}
              </Box>
              <Typography variant="body2" sx={{ mb: 1.5, color: "text.primary", lineHeight: 1.4 }}>
                {typeof item.evidence === 'object' ? (item.evidence.description || item.evidence.content || 'Evidence available') : item.evidence}
              </Typography>
              {item.source_url && (
                <Link href={item.source_url} target="_blank" sx={{ fontSize: "0.75rem", display: "flex", alignItems: "center" }}>
                  <LaunchIcon sx={{ fontSize: 12, mr: 0.5 }} />
                  View Details
                </Link>
              )}
            </Box>
          ))}
        </Box>
      );
    };



    // eslint-disable-next-line no-unused-vars
    const renderTechRoadmap = () => {
      const roadmap = intelligenceData.tech_roadmap;
      if (!roadmap || roadmap.length === 0) {
        return (
          <Box sx={{ textAlign: "center", py: 2 }}>
            <Typography variant="body2" color="text.secondary">No tech roadmap data available</Typography>
          </Box>
        );
      }

      return (
        <Box>
          {roadmap.slice(0, 4).map((item, idx) => (
            <Box key={idx} sx={{ mb: 2, p: 1.5, bgcolor: "#e8f5e8", borderRadius: 1, border: "1px solid #4caf50" }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: "#2e7d32", mb: 0.5 }}>
                � {item.initiative}
              </Typography>
              <Typography variant="body2" sx={{ mb: 1, color: "text.secondary" }}>
                {item.description}
              </Typography>
              <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                {item.timeline && (
                  <Typography variant="caption" sx={{ color: "text.secondary", fontWeight: 500 }}>
                    ⏱️ {item.timeline}
                  </Typography>
                )}
                {item.source_url && (
                  <Link href={item.source_url} target="_blank" sx={{ fontSize: "0.75rem", display: "flex", alignItems: "center" }}>
                    <LaunchIcon sx={{ fontSize: 12, mr: 0.5 }} />
                    Source
                  </Link>
                )}
              </Box>
            </Box>
          ))}
        </Box>
      );
    };

    return (
      <Card 
        elevation={0} 
        sx={{ 
          borderRadius: 0, 
          bgcolor: "white", 
          border: "none",
          height: "380px",
          display: "flex",
          flexDirection: "column",
          boxShadow: "none"
        }}
      >
        <CardContent sx={{ p: 1.5, flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          {/* Fixed Header */}
          <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between", mb: 1, flexShrink: 0 }}>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <SmartToyIcon sx={{ fontSize: 24, color: "#1976d2", mr: 0.8 }} />
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: "#1976d2", fontSize: "0.9rem", lineHeight: 1.1 }}>
                  🧠 AI Intelligence Dashboard
                </Typography>
                <Typography variant="caption" sx={{ color: "text.secondary", fontSize: "0.65rem", lineHeight: 1 }}>
                  Comprehensive business intelligence from web sources
                </Typography>
              </Box>
            </Box>
            <Chip 
              label={`Confidence: ${Math.round((intelligenceData.confidence_score || 0) * 100)}%`}
              size="small"
              color={intelligenceData.confidence_score > 0.7 ? "success" : intelligenceData.confidence_score > 0.4 ? "warning" : "error"}
              sx={{ fontWeight: 600, fontSize: "0.65rem", height: "20px" }}
            />
          </Box>

          {/* Scrollable Content Area - Paragraph Style Layout */}
          <Box sx={{ 
            flex: 1,
            overflowY: "auto",
            pr: 2,
            pl: 1,
            "&::-webkit-scrollbar": { width: "6px" },
            "&::-webkit-scrollbar-track": { bgcolor: "#f5f5f5", borderRadius: "3px" },
            "&::-webkit-scrollbar-thumb": { bgcolor: "#1976d260", borderRadius: "3px", "&:hover": { bgcolor: "#1976d2" } }
          }}>
            
            {/* Show message if no data is available at all */}
            {!((intelligenceData.annual_revenue || intelligenceData.employee_count || intelligenceData.market_position || intelligenceData.industry_focus) ||
               ((intelligenceData.technologies && intelligenceData.technologies.length > 0) || 
                (intelligenceData.tech_confirmed && intelligenceData.tech_confirmed.length > 0) ||
                (intelligenceData.tech_inferred && intelligenceData.tech_inferred.length > 0) ||
                intelligenceData.it_infrastructure_summary) ||
               ((intelligenceData.vendors && intelligenceData.vendors.length > 0) || 
                (intelligenceData.partnerships && intelligenceData.partnerships.length > 0) ||
                (intelligenceData.vendors_confirmed && intelligenceData.vendors_confirmed.length > 0) ||
                (intelligenceData.vendors_inferred && intelligenceData.vendors_inferred.length > 0)) ||
               ((intelligenceData.recent_announcements && intelligenceData.recent_announcements.length > 0) ||
                (intelligenceData.announcements && intelligenceData.announcements.length > 0) ||
                (intelligenceData.projects && intelligenceData.projects.length > 0)) ||
               (intelligenceData.business_context || intelligenceData.strategic_focus || 
                (intelligenceData.focus_areas && intelligenceData.focus_areas.length > 0))) && (
              <Box sx={{ 
                display: "flex", 
                flexDirection: "column", 
                alignItems: "center", 
                justifyContent: "center", 
                height: "300px", 
                textAlign: "center",
                color: "#666" 
              }}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: "#999" }}>
                  🔍 Limited Intelligence Data Available
                </Typography>
                <Typography variant="body2" sx={{ maxWidth: "80%", lineHeight: 1.6 }}>
                  The AI search found minimal business intelligence for this company. Try refining your search terms or the company may have limited online presence.
                </Typography>
              </Box>
            )}
            
            {/* Market Summary Section - Only show if data exists */}
            {(intelligenceData.annual_revenue || intelligenceData.employee_count || intelligenceData.market_position || intelligenceData.industry_focus) && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6" sx={{ 
                  display: "flex", 
                  alignItems: "center", 
                  color: "#2e7d32", 
                  fontWeight: 700, 
                  fontSize: "0.85rem",
                  mb: 1,
                  borderBottom: "1px solid #2e7d32",
                  pb: 0.3
                }}>
                  <TrendingUpIcon sx={{ mr: 0.8, fontSize: 16 }} />
                  Market Summary & Financial Overview
                </Typography>
                {renderFinancialContentParagraph()}
              </Box>
            )}

            {/* Technology & Infrastructure Section - Only show if data exists */}
            {((intelligenceData.technologies && intelligenceData.technologies.length > 0) || 
              (intelligenceData.tech_confirmed && intelligenceData.tech_confirmed.length > 0) ||
              (intelligenceData.tech_inferred && intelligenceData.tech_inferred.length > 0) ||
              intelligenceData.it_infrastructure_summary) && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6" sx={{ 
                  display: "flex", 
                  alignItems: "center", 
                  color: "#1976d2", 
                  fontWeight: 700, 
                  fontSize: "0.85rem",
                  mb: 1,
                  borderBottom: "1px solid #1976d2",
                  pb: 0.3
                }}>
                  <DevicesIcon sx={{ mr: 0.8, fontSize: 16 }} />
                  Technology Stack & IT Infrastructure
                </Typography>
                {renderTechnologyContentParagraph()}
              </Box>
            )}

            {/* Vendors & Partnership Section - Only show if data exists */}
            {((intelligenceData.vendors && intelligenceData.vendors.length > 0) || 
              (intelligenceData.partnerships && intelligenceData.partnerships.length > 0) ||
              (intelligenceData.vendors_confirmed && intelligenceData.vendors_confirmed.length > 0) ||
              (intelligenceData.vendors_inferred && intelligenceData.vendors_inferred.length > 0)) && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6" sx={{ 
                  display: "flex", 
                  alignItems: "center", 
                  color: "#ed6c02", 
                  fontWeight: 700, 
                  fontSize: "0.85rem",
                  mb: 1,
                  borderBottom: "1px solid #ed6c02",
                  pb: 0.3
                }}>
                  <PartnershipIcon sx={{ mr: 0.8, fontSize: 16 }} />
                  Vendor Details & Strategic Partners
                </Typography>
                {renderVendorsContentParagraph()}
              </Box>
            )}

            {/* Recent News & Announcements Section - Only show if data exists */}
            {((intelligenceData.recent_announcements && intelligenceData.recent_announcements.length > 0) ||
              (intelligenceData.announcements && intelligenceData.announcements.length > 0) ||
              (intelligenceData.projects && intelligenceData.projects.length > 0)) && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6" sx={{ 
                  display: "flex", 
                  alignItems: "center", 
                  color: "#d32f2f", 
                  fontWeight: 700, 
                  fontSize: "0.85rem",
                  mb: 1,
                  borderBottom: "1px solid #d32f2f",
                  pb: 0.3
                }}>
                  <AnnouncementIcon sx={{ mr: 0.8, fontSize: 16 }} />
                  Recent News & Market Announcements
                </Typography>
                {renderAnnouncementsContentParagraph()}
              </Box>
            )}

            {/* Strategic Focus & Business Context Section - Only show if data exists */}
            {(intelligenceData.business_context || intelligenceData.strategic_focus || 
              (intelligenceData.focus_areas && intelligenceData.focus_areas.length > 0)) && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6" sx={{ 
                  display: "flex", 
                  alignItems: "center", 
                  color: "#7b1fa2", 
                  fontWeight: 700, 
                  fontSize: "0.85rem",
                  mb: 1,
                  borderBottom: "1px solid #7b1fa2",
                  pb: 0.3
                }}>
                  <TargetIcon sx={{ mr: 0.8, fontSize: 16 }} />
                  Strategic Focus & Business Intelligence
                </Typography>
                {renderBusinessContextParagraph()}
              </Box>
            )}

          </Box>
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ bgcolor: "#f5f7fa", minHeight: "100vh", width: "100vw", px: 0, py: 0 }}>

      {/* Top Section: Input Parameters and AI Intelligence Dashboard side-by-side */}
      <Box sx={{ 
        display: "flex", 
        gap: 0, 
        mb: 0, 
        minHeight: "380px",
        alignItems: "stretch",
        width: "100%"
      }}>
        {/* Input Parameters Card - Left Side */}
        <Box sx={{ 
          width: "50%", 
          display: "flex", 
          flexDirection: "column",
          flex: "1 1 50%"
        }}>
          <Card 
            elevation={0} 
            sx={{ 
              borderRadius: 0, 
              bgcolor: "white",
              height: "380px",
              display: "flex",
              flexDirection: "column",
              boxShadow: "none",
              borderRight: "1px solid #e0e0e0"
            }}
          >
            <CardContent sx={{ flex: 1, display: "flex", flexDirection: "column", p: 2.5 }}>
              {/* Moved heading into card */}
              <Box sx={{ mb: 2, pb: 1.5, borderBottom: "1px solid #e3f2fd" }}>
                <Typography variant="h6" sx={{ fontWeight: 700, color: "#1976d2", mb: 0.5 }}>
                  {localCustomer ? `${localCustomer} – Pitch Generation` : "Portfolio Pitch Generation"}
                </Typography>
                <Typography variant="body2" sx={{ color: "#666", fontSize: "0.9rem" }}>
                  Build a tailored pitch for your customer using portfolio intelligence.
                </Typography>
              </Box>
              
              <Typography variant="h6" sx={{ mb: 1.5, fontWeight: 600, color: "#1976d2", fontSize: "1rem" }}>
                🎯 Customer Information
              </Typography>
              
              <Grid container spacing={1.5} sx={{ flex: 1 }}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Customer Name"
                    value={localCustomer}
                    onChange={(e) => setLocalCustomer(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        handleIndustryDetection();
                      }
                    }}
                    variant="outlined"
                    size="small"
                    helperText={detectingIndustry ? "Detecting industry..." : "Press Enter to detect industry"}
                    sx={{ "& .MuiFormHelperText-root": { fontSize: "0.75rem", mt: 0.5 } }}
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <Box>
                    <TextField
                      fullWidth
                      label="Industry"
                      value={industry}
                      onChange={(e) => {
                        setIndustry(e.target.value);
                        setIndustryConfidence(null); // Clear confidence when manually editing
                      }}
                      variant="outlined"
                      size="small"
                    />
                    {industryConfidence !== null && (
                      <Box sx={{ mt: 0.3 }}>
                        <Chip
                          label={`Confidence: ${Math.round(industryConfidence * 100)}%`}
                          size="small"
                          color={industryConfidence > 0.8 ? "success" : industryConfidence > 0.6 ? "warning" : "error"}
                          sx={{ fontSize: "0.65rem", height: "18px" }}
                        />
                      </Box>
                    )}
                  </Box>
                </Grid>

                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Technology Focus"
                    value={technology}
                    onChange={(e) => setTechnology(e.target.value)}
                    variant="outlined"
                    size="small"
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Business Focus"
                    value={focus}
                    onChange={(e) => setFocus(e.target.value)}
                    variant="outlined"
                    size="small"
                  />
                </Grid>
                
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Row Limit"
                    type="number"
                    value={limit}
                    onChange={(e) => setLimit(Math.max(1, parseInt(e.target.value) || 6))}
                    variant="outlined"
                    size="small"
                    inputProps={{ min: 1, max: 20 }}
                  />
                </Grid>

                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Website (optional)"
                    value={companyWebsite}
                    onChange={(e) => setCompanyWebsite(e.target.value)}
                    variant="outlined"
                    size="small"
                  />
                </Grid>
              </Grid>
              
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  size="medium"
                  startIcon={<SearchIcon />}
                  onClick={handleFetchRows}
                  disabled={loading}
                  fullWidth
                  sx={{ borderRadius: 2, py: 1, fontSize: "0.9rem" }}
                >
                  {loading ? "Analyzing & Fetching..." : "🔍 Analyze & Fetch Portfolio Matches"}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>

        {/* AI Intelligence Dashboard Card - Right Side */}
        <Box sx={{ 
          width: "50%", 
          display: "flex", 
          flexDirection: "column",
          flex: "1 1 50%",
          minHeight: "380px",
          maxHeight: "380px"
        }}>
          {intelligenceData && !loading ? (
            renderAIIntelligenceDashboard()
          ) : (
            <Card 
              elevation={0} 
              sx={{ 
                borderRadius: 0, 
                bgcolor: "#f8f9fa",
                height: "380px",
                display: "flex",
                flexDirection: "column",
                boxShadow: "none",
                border: "1px solid #e0e0e0"
              }}
            >
              <CardContent sx={{ 
                flex: 1, 
                display: "flex", 
                flexDirection: "column", 
                justifyContent: "center", 
                alignItems: "center",
                textAlign: "center",
                p: 4
              }}>
                <SmartToyIcon sx={{ fontSize: 60, color: "#bdbdbd", mb: 2 }} />
                <Typography variant="h6" sx={{ fontWeight: 600, color: "#666", mb: 1 }}>
                  🧠 AI Intelligence Dashboard
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ maxWidth: "300px" }}>
                  Enter a customer name and click "Analyze & Fetch Portfolio Matches" to see comprehensive business intelligence from web sources.
                </Typography>
                {loading && (
                  <Box sx={{ mt: 3, display: "flex", flexDirection: "column", alignItems: "center" }}>
                    <CircularProgress size={40} />
                    <Typography variant="caption" sx={{ mt: 1, color: "#666" }}>
                      Gathering intelligence...
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          )}
        </Box>
      </Box>

      {loading && <Loader />}

      {matchedRows.length > 0 && (
        <Box sx={{ 
          display: "flex", 
          gap: 2, 
          minHeight: "75vh",
          width: "100vw",
          alignItems: "stretch"
        }}>
          <Box sx={{ 
            width: "50%", 
            display: "flex", 
            flexDirection: "column",
            flex: "1 1 50%"
          }}>
            <Card
              elevation={0}
              sx={{
                borderRadius: 0,
                bgcolor: "white",
                height: "700px", // Increased height to match right card for better content display
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
                boxShadow: "none",
                borderRight: "1px solid #e0e0e0"
              }}
            >
              <CardContent sx={{ flex: 1, display: "flex", flexDirection: "column", p: 2 }}>
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 700, color: "#1976d2" }}>
                    📋 Excel Fetched Rows ({matchedRows.length}) {matchedRows.length > 4 ? "⬇️ Scroll" : ""}
                  </Typography>
                  <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                    <Chip 
                      label={`Limit: ${limit}`} 
                      size="small" 
                      color="primary" 
                      variant="outlined"
                      sx={{ fontSize: "0.75rem" }}
                    />
                    <Button size="small" variant="outlined" onClick={handleSelectAll}>
                      {selectedRowIndices.length === matchedRows.length ? "Deselect All" : "Select All"}
                    </Button>
                  </Box>
                </Box>

                <Box
                  sx={{
                    flex: 1,
                    overflowY: "auto", // Enable vertical scrolling for parent
                    overflowX: "hidden", // Prevent horizontal scroll
                    pr: 1,
                    minHeight: 0, // Critical for flex child scrolling
                    maxHeight: "650px", // Increased height to extend closer to Build Pitch button
                    "&::-webkit-scrollbar": { 
                      width: "6px" // Thinner scrollbar for less visual prominence
                    },
                    "&::-webkit-scrollbar-track": { 
                      bgcolor: "#f1f3f4", 
                      borderRadius: "6px",
                      margin: "1px"
                    },
                    "&::-webkit-scrollbar-thumb": { 
                      bgcolor: "#bdc3c7", // Subtle gray color
                      borderRadius: "6px",
                      border: "1px solid #f1f3f4",
                      "&:hover": { 
                        bgcolor: "#95a5a6" // Slightly darker on hover
                      }
                    },
                    "&::-webkit-scrollbar-corner": {
                      bgcolor: "#f1f3f4"
                    }
                  }}
                >
                  {matchedRows.map((row, idx) => renderMatchedRow(row, idx))}
                </Box>
              </CardContent>
            </Card>

            <Button
              variant="contained"
              color="success"
              size="large"
              fullWidth
              onClick={handleBuildPitch}
              disabled={selectedRowIndices.length === 0 || loading}
              startIcon={<SummarizeIcon />}
              sx={{ 
                mt: 2, 
                borderRadius: 2, 
                py: 1.5, 
                fontWeight: 600, 
                fontSize: "1.05rem",
                boxShadow: 3
              }}
            >
              {loading ? "Building..." : `Build Pitch (${selectedRowIndices.length} selected)`}
            </Button>
          </Box>

          <Box sx={{ 
            width: "50%", 
            display: "flex", 
            flexDirection: "column",
            flex: "1 1 50%"
          }}>
            <Card
              elevation={0}
              sx={{
                borderRadius: 0,
                bgcolor: "white",
                height: "700px", // Increased height to accommodate both summaries properly
                display: "flex",
                flexDirection: "column",
                overflow: "hidden",
                boxShadow: "none"
              }}
            >
              <CardContent sx={{ flex: 1, display: "flex", flexDirection: "column", p: 2 }}>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 700, color: "#1976d2" }}>
                  📄 Generated Pitch Summary
                </Typography>
                
                <Box 
                  sx={{ 
                    flex: 1, 
                    overflowY: "auto", 
                    pr: 1,
                    pb: 2, // Add bottom padding to prevent content from being hidden
                    "&::-webkit-scrollbar": { width: "8px" },
                    "&::-webkit-scrollbar-track": { bgcolor: "#f1f1f1", borderRadius: "10px" },
                    "&::-webkit-scrollbar-thumb": { bgcolor: "#888", borderRadius: "10px" },
                    "&::-webkit-scrollbar-thumb:hover": { bgcolor: "#555" }
                  }}
                >
                  {renderPitchSummaryContent()}
                </Box>
              </CardContent>
            </Card>

            {pitchGenerated && (
              <Box sx={{ mt: 2 }}>
                <Grid container spacing={3} sx={{ mb: 3 }}>
                  <Grid item xs={6}>
                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={<DownloadIcon />}
                      onClick={handleDownloadPitch}
                      fullWidth
                      size="large"
                      sx={{ borderRadius: 2, py: 1.5, fontWeight: 600, boxShadow: 3 }}
                    >
                      Download PDF
                    </Button>
                  </Grid>
                  <Grid item xs={6}>
                    <Button
                      variant="contained"
                      color="secondary"
                      startIcon={refining ? <CircularProgress size={20} color="inherit" /> : <AutoFixHighIcon />}
                      onClick={handleRefinePitch}
                      disabled={refining || !refinementInstructions.trim()}
                      fullWidth
                      size="large"
                      sx={{ borderRadius: 2, py: 1.5, fontWeight: 600, boxShadow: 3 }}
                    >
                      {refining ? "Refining..." : "Refine Summary"}
                    </Button>
                  </Grid>
                </Grid>

                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" sx={{ mb: 1, color: "#666", fontWeight: 600 }}>
                    ✨ Enhancement Instructions
                  </Typography>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    variant="outlined"
                    placeholder="e.g., 'short summary in 300 words' or 'add more ROI focus' or 'emphasize cloud migration benefits'"
                    value={refinementInstructions}
                    onChange={(e) => setRefinementInstructions(e.target.value)}
                    sx={{ bgcolor: "white", borderRadius: 2 }}
                    helperText="Describe changes you'd like (word count, focus areas, technical depth, etc.)"
                  />
                </Box>
              </Box>
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
}