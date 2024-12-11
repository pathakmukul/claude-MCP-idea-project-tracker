# claude-MCP-idea-project-tracker

# Claude MCP IdeaFlow Project Tracker

## Overview
**Claude MCP IdeaFlow Project Tracker** is a powerful tool designed to help users manage their project ideas and workflows seamlessly. Built on the Model Context Protocol (MCP), this application allows users to scan their folders for ongoing projects, store relevant data in an SQLite database, and interact with Claude to enhance their project management experience.

## Key Features

### 1. Project Scanning
- **Automatic Folder Scanning**: The tool scans user-defined directories to identify ongoing projects.
- **Data Storage**: Captured project details are stored in an SQLite database for easy access and management.

### 2. Interactive Idea Management
- **Chat with Claude**: Users can interact with Claude to add new ideas or enhance existing ones.
- **Add to Idea Store**: Simply say "add to idea store" during a conversation to summarize and store the discussion in the database.

### 3. Comprehensive Project Data
The application can manage the following project attributes:
- **Project Name**: The name of the project.
- **Category**: The category of the project (e.g., Software, Research).
- **Priority Level**: A number indicating the project's priority (1-4).
- **Size Score**: A score indicating the project's size (1-3).
- **Business Impact**: A score indicating the potential business impact (1-4).
- **Resource Type**: A number indicating the type of resources required (1-3).
- **Risk Level**: A number indicating the project's risk level (1-3).
- **Project Phase**: The current phase of the project (Planning, In Progress, On Hold, Completed).
- **Notes**: Additional notes related to the project.

### 4. Visual Dashboard
- **Streamlit Dashboard**: An interactive dashboard built with Streamlit to visualize project data, including metrics, distributions, and detailed project information.

## Getting Started

### Prerequisites
- Python 3.x
- Node.js
- SQLite

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/claude-MCP-ideaflow-project-tracker.git
   cd claude-MCP-ideaflow-project-tracker
   ```

2. **Set up the backend:**
   - Navigate to the `src` directory and install the required packages:
   ```bash
   npm install
   ```

3. **Set up the database:**
   - Run the SQL schema to create the necessary tables:
   ```bash
   sqlite3 data/project_tracker.db < src/db/schema.sql
   ```

4. **Install Python dependencies:**
   - Create a virtual environment and install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the MCP server:**
   ```bash
   npm run start
   ```

2. **Run the dashboard:**
   ```bash
   streamlit run src/dashboard.py
   ```

3. **Access the dashboard:**
   - Open your web browser and go to `http://localhost:8501` to view the dashboard.

## Usage

- **Scan Projects**: Automatically scan your folders for ongoing projects and store their details.
- **Interact with Claude**: Use natural language to add or enhance project ideas.
- **Visualize Data**: Use the dashboard to gain insights into your project portfolio.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Streamlit and Plotly communities for their amazing tools.
- Special thanks to Claude for providing AI-driven insights and enhancements.

---

*Because every great project starts with an idea - make yours count!*
