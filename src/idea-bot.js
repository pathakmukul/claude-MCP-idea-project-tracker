#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema, } from "@modelcontextprotocol/sdk/types.js";
import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import path from 'path';
// Database helper
async function getDb() {
    return open({
        filename: path.join(process.cwd(), 'data', 'project_tracker.db'),
        driver: sqlite3.Database
    });
}
// Tool definitions
const ADD_IDEA_TOOL = {
    name: "idea_bot_add",
    description: "Add a new project idea to the database with details like name, category, priority, etc.",
    inputSchema: {
        type: "object",
        properties: {
            project_name: { type: "string" },
            category: { type: "string" },
            priority_level: { type: "number", minimum: 1, maximum: 4 },
            size_score: { type: "number", minimum: 1, maximum: 3 },
            business_impact: { type: "number", minimum: 1, maximum: 4 },
            resource_type: { type: "number", minimum: 1, maximum: 3 },
            risk_level: { type: "number", minimum: 1, maximum: 3 },
            project_phase: { type: "string", enum: ["Planning", "In Progress", "On Hold", "Completed"] },
            notes: { type: "string" }
        },
        required: ["project_name", "category"]
    }
};
const GET_IDEA_TOOL = {
    name: "idea_bot_get",
    description: "Retrieve project ideas with optional filters for category, phase, or priority level",
    inputSchema: {
        type: "object",
        properties: {
            project_name: { type: "string" },
            category: { type: "string" },
            project_tier: { type: "number" },
            project_phase: { type: "string" }
        }
    }
};
const ARTIFACT_TOOL = {
    name: "idea_artifact",
    description: "Generate visualization from idea_store data",
    inputSchema: {
        type: "object",
        properties: {
            view_type: {
                type: "string",
                enum: ["all", "priority", "category", "phase"],
                default: "all"
            }
        }
    }
};
// Initialize server
const server = new Server({
    name: "idea-bot-server",
    version: "0.1.0",
}, {
    capabilities: {
        tools: {},
    },
});
// Register tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools: [
        ADD_IDEA_TOOL,
        GET_IDEA_TOOL,
        {
            ...ARTIFACT_TOOL,
            description: "Generate visualization from idea_store table data (provided as JSON in response)"
        }
    ]
}));
// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args = {} } = request.params;
    try {
        const db = await getDb();
        if (name === "idea_bot_add") {
            const result = await db.run(`
        INSERT INTO idea_store (
          project_name, category, priority_level, size_score, 
          business_impact, resource_type, risk_level, project_phase, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      `, [
                args.project_name,
                args.category,
                args.priority_level || 1,
                args.size_score || 1,
                args.business_impact || 1,
                args.resource_type || 1,
                args.risk_level || 1,
                args.project_phase || 'Planning',
                args.notes || ''
            ]);
            return {
                content: [{
                        type: "text",
                        text: `Added project "${args.project_name}" to database`
                    }],
                isError: false,
            };
        }
        if (name === "idea_bot_get") {
            let query = `SELECT * FROM idea_store WHERE 1=1`;
            const params = [];
            if (args.project_name) {
                query += ` AND project_name LIKE ?`;
                params.push(`%${args.project_name}%`);
            }
            if (args.category) {
                query += ` AND category = ?`;
                params.push(args.category);
            }
            if (args.project_tier) {
                query += ` AND project_tier = ?`;
                params.push(args.project_tier);
            }
            if (args.project_phase) {
                query += ` AND project_phase = ?`;
                params.push(args.project_phase);
            }
            const ideas = await db.all(query, params);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify(ideas, null, 2)
                    }],
                isError: false,
            };
        }
        if (name === "idea_artifact") {
            const ideas = await db.all('SELECT * FROM idea_store ORDER BY priority_level DESC, total_score DESC');
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            data: ideas,
                            visualization_instructions: {
                                type: args.view_type,
                                style: "futuristic-neon",
                                elements: [
                                    "hexagonal-grid",
                                    "priority-matrix",
                                    "pipeline-view",
                                    "risk-heatmap",
                                    "resource-allocation"
                                ]
                            }
                        }, null, 2)
                    }],
                isError: false,
            };
        }
        return {
            content: [{
                    type: "text",
                    text: `Unknown tool: ${name}`
                }],
            isError: true,
        };
    }
    catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
        return {
            content: [{
                    type: "text",
                    text: `Error: ${errorMessage}`
                }],
            isError: true,
        };
    }
});
function generateDashboard(ideas, viewType) {
    // Just return the data as JSON for Claude to interpret
    return JSON.stringify({
        summary: {
            total_count: ideas.length,
            high_priority_count: ideas.filter(p => p.priority_level >= 3).length,
            average_score: ideas.reduce((sum, p) => sum + p.total_score, 0) / ideas.length
        },
        categories: ideas.reduce((acc, p) => {
            acc[p.category] = (acc[p.category] || 0) + 1;
            return acc;
        }, {}),
        phases: ideas.reduce((acc, p) => {
            acc[p.project_phase] = (acc[p.project_phase] || 0) + 1;
            return acc;
        }, {}),
        priority_projects: ideas
            .filter(p => p.priority_level >= 3)
            .sort((a, b) => b.total_score - a.total_score)
            .map(p => ({
            name: p.project_name,
            score: p.total_score,
            category: p.category,
            phase: p.project_phase,
            impact: p.business_impact,
            risk: p.risk_level
        })),
        risk_levels: {
            high: ideas.filter(p => p.risk_level === 3).length,
            medium: ideas.filter(p => p.risk_level === 2).length,
            low: ideas.filter(p => p.risk_level === 1).length
        },
        resource_types: {
            internal: ideas.filter(p => p.resource_type === 1).length,
            external: ideas.filter(p => p.resource_type === 2).length,
            mixed: ideas.filter(p => p.resource_type === 3).length
        }
    }, null, 2);
}
// Start the server
async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("Idea Bot MCP Server running on stdio");
}
main().catch((error) => {
    console.error("Fatal error:", error);
    process.exit(1);
});
