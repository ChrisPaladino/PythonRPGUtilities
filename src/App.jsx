import React, { useState } from 'react'
import { Container, Tabs, Tab, Box } from '@mui/material'
import ThemesTab from './components/ThemesTab'
import FateTab from './components/FateTab'
import CharactersTab from './components/CharactersTab'

function App() {
  const [currentTab, setCurrentTab] = useState(0)

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue)
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={currentTab} onChange={handleTabChange}>
          <Tab label="Themes" />
          <Tab label="Fate & Oracles" />
          <Tab label="Characters & Threads" />
        </Tabs>
      </Box>

      <Box sx={{ mt: 2 }}>
        {currentTab === 0 && <ThemesTab />}
        {currentTab === 1 && <FateTab />}
        {currentTab === 2 && <CharactersTab />}
      </Box>
    </Container>
  )
}

export default App