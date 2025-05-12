import React, { useState } from 'react'
import { Box, Button, List, ListItem, ListItemText, Paper, Typography } from '@mui/material'

const defaultThemes = ["Action", "Mystery", "Personal", "Social", "Tension"]

function ThemesTab() {
  const [themes, setThemes] = useState(defaultThemes)
  const [output, setOutput] = useState([])

  const moveTheme = (index, direction) => {
    if ((direction === -1 && index === 0) || (direction === 1 && index === themes.length - 1)) {
      return
    }
    const newThemes = [...themes]
    const temp = newThemes[index]
    newThemes[index] = newThemes[index + direction]
    newThemes[index + direction] = temp
    setThemes(newThemes)
  }

  const generateThemes = () => {
    const weights = [40, 30, 20, 8, 2]
    const results = themes.map((theme, index) => {
      const roll = Math.floor(Math.random() * 100) + 1
      return `Theme: ${theme}, Weight: ${weights[index]}%, Roll: ${roll}`
    })
    setOutput(results)
  }

  const resetOrder = () => {
    setThemes([...defaultThemes])
  }

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 2 }}>
        <List>
          {themes.map((theme, index) => (
            <ListItem key={theme}>
              <ListItemText primary={theme} />
              <Button 
                disabled={index === 0} 
                onClick={() => moveTheme(index, -1)}
              >
                Move Up
              </Button>
              <Button 
                disabled={index === themes.length - 1} 
                onClick={() => moveTheme(index, 1)}
              >
                Move Down
              </Button>
            </ListItem>
          ))}
        </List>
      </Paper>

      <Box sx={{ mb: 2 }}>
        <Button variant="contained" onClick={generateThemes} sx={{ mr: 1 }}>
          Generate Themes
        </Button>
        <Button variant="outlined" onClick={resetOrder}>
          Reset Order
        </Button>
      </Box>

      <Paper sx={{ p: 2, minHeight: 200, maxHeight: 400, overflow: 'auto' }}>
        {output.map((result, index) => (
          <Typography key={index} paragraph>
            {result}
          </Typography>
        ))}
      </Paper>
    </Box>
  )
}

export default ThemesTab