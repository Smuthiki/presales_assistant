




import React, { useState } from "react";
import { Tabs, Tab, Box } from "@mui/material";
import SummarizeIcon from "@mui/icons-material/Summarize";
import ListAltIcon from "@mui/icons-material/ListAlt";
import FolderSpecialIcon from "@mui/icons-material/FolderSpecial";
import ChatIcon from "@mui/icons-material/Chat";
import Header from "./components/Header";
import PortfolioSummaryEnhanced from "./components/PortfolioSummary";
import CaseStudiesSummary from "./components/CaseStudiesSummary";
import ChatSection from "./components/ChatSection";

function App() {
  const [customer] = useState("");
  const [industry] = useState("");
  const [tab, setTab] = useState(0);
  const [detectedIndustry] = useState("");

  return (
    <Box sx={{ width: "100vw", minHeight: "100vh", overflow: "hidden" }}>
      <Header />
      <Box sx={{ bgcolor: "#1976d2", borderRadius: 0, mb: 0, width: "100vw", boxShadow: "0 2px 8px rgba(0,0,0,0.15)" }}>
        <Tabs
          value={tab}
          onChange={(e, newTab) => setTab(newTab)}
          variant="fullWidth"
          sx={{
            bgcolor: "#1976d2",
            borderRadius: 0,
            mb: 0,
            width: "100%",
            minHeight: "64px",
            "& .MuiTab-root": { 
              color: "rgba(255, 255, 255, 0.7)", 
              fontWeight: "bold",
              fontSize: "0.9rem",
              minHeight: "64px",
              padding: "12px 16px",
              textTransform: "none",
              transition: "all 0.3s ease-in-out",
              borderRight: "1px solid rgba(255, 255, 255, 0.1)",
              "&:hover": {
                bgcolor: "rgba(255, 255, 255, 0.1)",
                color: "rgba(255, 255, 255, 0.9)",
                transform: "translateY(-1px)",
                boxShadow: "0 4px 8px rgba(0,0,0,0.2)"
              },
              "&:last-child": {
                borderRight: "none"
              }
            },
            "& .Mui-selected": { 
              color: "#fff !important",
              bgcolor: "rgba(255, 255, 255, 0.15) !important",
              boxShadow: "inset 0 2px 4px rgba(0,0,0,0.1), 0 4px 8px rgba(0,0,0,0.2)",
              borderBottom: "3px solid #ffeb3b",
              fontWeight: "800",
              "&:hover": {
                bgcolor: "rgba(255, 255, 255, 0.2) !important",
                transform: "none"
              }
            },
            "& .MuiTabs-indicator": { 
              backgroundColor: "#ffeb3b",
              height: "3px",
              borderRadius: "2px 2px 0 0"
            }
          }}
        >
          <Tab icon={<SummarizeIcon />} label="📊 Portfolio Summary" />
          <Tab icon={<ListAltIcon />} label="📝 Portfolio Selected" />
          <Tab icon={<FolderSpecialIcon />} label="📁 Case Studies Pitch" />
          <Tab icon={<ChatIcon />} label="💬 Chat Assistant" />
        </Tabs>
      </Box>

      {tab === 0 && (
        <PortfolioSummaryEnhanced customer={customer} detectedIndustry={detectedIndustry} />
      )}

      {tab === 1 && (
        <Box sx={{ bgcolor: "#fce4ec", p: 3, borderRadius: 0, mb: 0, width: "100vw" }}>
          <strong>Portfolio Summary Selected</strong>
          <br />
          <em>Feature coming soon!</em>
        </Box>
      )}

      {tab === 2 && (
        <CaseStudiesSummary customer={customer} industry={industry} />
      )}

      {tab === 3 && (
        <ChatSection customer={customer} industry={industry} />
      )}
    </Box>
  );
}

export default App;