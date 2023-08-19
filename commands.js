import 'dotenv/config';
import { getRPSChoices } from './game.js';
import { capitalize, InstallGlobalCommands } from './utils.js';

// Get the game choices from game.js
function createCommandChoices() {
  const choices = getRPSChoices();
  const commandChoices = [];

  for (let choice of choices) {
    commandChoices.push({
      name: capitalize(choice),
      value: choice.toLowerCase(),
    });
  }

  return commandChoices;
}

const CARD_COMMAND = {
  name: 'card',
  description: 'Generates a card for the player you specify.',
  type: 1,
};

const REGISTER_COMMAND = {
  name: 'register',
  description: 'Links your minecraft account with your discord account.',
  type: 1,
};

const UNREGISTER_COMMAND = {
  name: 'unregister',
  description: 'Unlinks your minecraft account with your discord account.',
  type: 1,
};

// Simple test command
const TEST_COMMAND = {
  name: 'test',
  description: 'Basic command',
  type: 1,
};

// Command containing options
const CHALLENGE_COMMAND = {
  name: 'challenge',
  description: 'Challenge to a match of rock paper scissors',
  options: [
    {
      type: 3,
      name: 'object',
      description: 'Pick your object',
      required: true,
      choices: createCommandChoices(),
    },
  ],
  type: 1,
};

const ALL_COMMANDS = [CARD_COMMAND, REGISTER_COMMAND, UNREGISTER_COMMAND, TEST_COMMAND, CHALLENGE_COMMAND];

InstallGlobalCommands(process.env.APP_ID, ALL_COMMANDS);