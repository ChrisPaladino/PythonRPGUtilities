import React, { useState } from 'react'
import { 
  Box, Typography, TextField, Button, FormControl, 
  InputLabel, Select, MenuItem, Paper, Grid 
} from '@mui/material'

function FateTab() {
  const [actionDice, setActionDice] = useState(1)
  const [dangerDice, setDangerDice] = useState(0)
  const [chaosFactor, setChaosFactor] = useState(5)
  const [likelihood, setLikelihood] = useState('50/50')
  const [output, setOutput] = useState([])

  const adjustDice = (type, delta) => {
    if (type === 'action') {
      setActionDice(Math.max(0, Math.min(10, actionDice + delta)))
    } else {
      setDangerDice(Math.max(0, Math.min(10, dangerDice + delta)))
    }
  }

  const rollDice = () => {
    const result = `Rolling ${actionDice} action dice and ${dangerDice} danger dice...`
    setOutput([result, ...output])
  }

  const rollFate = () => {
    const result = `Fate check with Chaos Factor ${chaosFactor} and likelihood ${likelihood}...`
    setOutput([result, ...output])
  }

  const generateNPC = () => {
    const result = "Generating NPC..."
    setOutput([result, ...output])
  }

  const clearOutput = () => {
    setOutput([])
  }

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>Dice Rolling</Typography>
            <Box sx={{ mb: 2 }}>
              <Typography>Action Dice: {actionDice}</Typography>
              <Button onClick={() => adjustDice('action', 1)} sx={{ mr: 1 }}>+</Button>
              <Button onClick={() => adjustDice('action', -1)}>-</Button>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography>Danger Dice: {dangerDice}</Typography>
              <Button onClick={() => adjustDice('danger', 1)} sx={{ mr: 1 }}>+</Button>
              <Button onClick={() => adjustDice('danger', -1)}>-</Button>
            </Box>
            <Button variant="contained" onClick={rollDice} sx={{ mr: 1 }}>Roll Dice</Button>
          </Paper>

          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>Fate Check</Typography>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Chaos Factor</InputLabel>
              <Select
                value={chaosFactor}
                label="Chaos Factor"
                onChange={(e) => setChaosFactor(e.target.value)}
              >
                {[1,2,3,4,5,6,7,8,9].map(n => (
                  <MenuItem key={n} value={n}>{n}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Likelihood</InputLabel>
              <Select
                value={likelihood}
                label="Likelihood"
                onChange={(e) => setLikelihood(e.target.value)}
              >
                {[
                  'Certain', 'Nearly Certain', 'Very Likely', 'Likely', 
                  '50/50', 'Unlikely', 'Very Unlikely', 'Nearly Impossible', 
                  'Impossible'
                ].map(option => (
                  <MenuItem key={option} value={option}>{option}</MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button variant="contained" onClick={rollFate}>Roll Fate</Button>
          </Paper>

          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>NPC Generation</Typography>
            <Button variant="contained" onClick={generateNPC}>Generate NPC</Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">Output</Typography>
              <Button onClick={clearOutput}>Clear</Button>
            </Box>
            <Box sx={{ maxHeight: 600, overflow: 'auto' }}>
              {output.map((text, index) => (
                <Typography key={index} paragraph>{text}</Typography>
              ))}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

export default FateTab