import React from "react";
import EmojiObjectsIcon from "@mui/icons-material/EmojiObjects";
import { Typography, Box } from "@mui/material";

export default function Header() {
  return (
    <Box sx={{ 
      bgcolor: "#1976d2", 
      color: "white", 
      px: 3, 
      py: 1.5, 
      mb: 0, 
      borderRadius: 0, 
      display: "flex", 
      alignItems: "center", 
      gap: 2,
      width: "100vw",
      position: "relative",
      left: "50%",
      right: "50%",
      marginLeft: "-50vw",
      marginRight: "-50vw"
    }}>
      <EmojiObjectsIcon fontSize="large" />
      <Typography variant="h4" sx={{ fontWeight: "bold" }}>
        Presales Assistant 🚀
      </Typography>
      <Typography variant="subtitle1" sx={{ ml: 2 }}>
        Your AI-powered sales pitch generator
      </Typography>
    </Box>
  );
}