import React from "react";
import { Box, Typography } from "@mui/material";

export default function Loader({ message = "Your response is on the way..." }) {
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        py: 2,
      }}
    >
      {/* Use relative path to public folder */}
      <img
        src="/Triple intersection.gif"
        alt="Loading animation"
        style={{ height: 40, marginRight: 12 }}
      />
      <Typography variant="subtitle1" sx={{ color: "#1976d2" }}>
        {message}
      </Typography>
    </Box>
  );
}
