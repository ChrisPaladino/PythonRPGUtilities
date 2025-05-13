import React, { useState } from 'react'
import { 
  Box, Typography, TextField, Button, List, 
  ListItem, ListItemText, Paper, Grid 
} from '@mui/material'

function CharactersTab() {
  const [characters, setCharacters] = useState([])
  const [threads, setThreads] = useState([])
  const [newCharacter, setNewCharacter] = useState('')
  const [newThread, setNewThread] = useState('')
  const [output, setOutput] = useState([])

  const addCharacter = () => {
    if (newCharacter.trim() && characters.length < 25) {
      setCharacters([...characters, newCharacter.trim()])
      setNewCharacter('')
    }
  }

  const addThread = () => {
    if (newThread.trim() && threads.length < 25) {
      setThreads([...threads, newThread.trim()])
      setNewThread('')
    }
  }

  const deleteCharacter = (index) => {
    const newCharacters = characters.filter((_, i) => i !== index)
    setCharacters(newCharacters)
  }

  const deleteThread = (index) => {
    const newThreads = threads.filter((_, i) => i !== index)
    setThreads(newThreads)
  }

  const chooseRandom = (type) => {
    const list = type === 'character' ? characters : threads
    if (list.length > 0) {
      const randomItem = list[Math.floor(Math.random() * list.length)]
      setOutput([`Selected ${type}: ${randomItem}`, ...output])
    }
  }

  const clearOutput = () => {
    setOutput([])
  }

  return (
    <Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>Characters</Typography>
            <Box sx={{ mb: 2 }}>
              <TextField
                fullWidth
                value={newCharacter}
                onChange={(e) => setNewCharacter(e.target.value)}
                placeholder="Enter character name"
                sx={{ mb: 1 }}
              />
              <Button variant="contained" onClick={addCharacter}>Add Character</Button>
            </Box>
            <List>
              {characters.map((character, index) => (
                <ListItem key={index}>
                  <ListItemText primary={character} />
                  <Button onClick={() => deleteCharacter(index)}>Delete</Button>
                </ListItem>
              ))}
            </List>
            <Button 
              variant="outlined" 
              onClick={() => chooseRandom('character')}
              disabled={characters.length === 0}
            >
              Choose Random Character
            </Button>
          </Paper>

          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Threads</Typography>
            <Box sx={{ mb: 2 }}>
              <TextField
                fullWidth
                value={newThread}
                onChange={(e) => setNewThread(e.target.value)}
                placeholder="Enter thread description"
                sx={{ mb: 1 }}
              />
              <Button variant="contained" onClick={addThread}>Add Thread</Button>
            </Box>
            <List>
              {threads.map((thread, index) => (
                <ListItem key={index}>
                  <ListItemText primary={thread} />
                  <Button onClick={() => deleteThread(index)}>Delete</Button>
                </ListItem>
              ))}
            </List>
            <Button 
              variant="outlined" 
              onClick={() => chooseRandom('thread')}
              disabled={threads.length === 0}
            >
              Choose Random Thread
            </Button>
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

export default CharactersTab