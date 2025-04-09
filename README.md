# time_tracker
This is a repo for a very simple time tracker that allows one to effortlessly track time to various projects throughout the day.

The basic wants for the time tracker:

## Core Time Tracking Features
- Per-project timers: Start/stop timers by clicking a project tile to track active time.
- Real-time second-level display: While only minutes are saved, the UI shows seconds ticking live for visibility.
- Auto-save: Project time data auto-saves every 15 minutes and on any time tick.
- Time of day tracking: Start and stop times are recorded for each project, each day.

## Calendar View
- Weekly calendar layout (Mon–Fri): Each weekday is selectable via button, showing that day's tracked data.
- Day-specific time logs: Time is stored per-project, per-day using localStorage.

## Project Management
- Add new projects via a prompt button.
- Editable project names: Click the ✎ icon to rename a project. Ensures names are unique. Changing the name of a project does not start or stop the currently tracked time.
- Delete project: Projects with < 10 minutes of tracked time are deleted from storage when removed.
- Color customization: 🎨 button allows setting a project’s color via hex/name, stored in localStorage.
- Auto-assigned unique colors: New projects receive rotating distinct default colors if none is set.

## Visual Feedback
- Active project indicator: Active project box is outlined with a thick pulsing dashed border.
- Live UI updates: Active timer updates every second in the UI (though storage remains per-minute).
- Inactive week indicators: Days that are not part of the current week have a dimmer color and have a padlock icon over them.

## Weekly Summary Chart
- Stacked bar chart using Chart.js: Displays total time per project across weekdays, as well as the start and stop times for each project for each day.
- Dynamic dataset loading: Chart auto-adjusts to new projects with tracked time. The chart always shows the five days of the week (Monday through Friday).
- Color-matched bars: Chart bars use the same color as the corresponding project.
- Stacked bars: Chart bars are stacked, first project to last project, to show the amount of time tracked for each project for each day.

## Data Export & Import
- CSV export: Generates a weekly_project_data.csv showing time per project, per weekday, as well as the start and stop times for each project.
- JSON export: Saves full weekly data (projectData_Monday...Friday) plus projectColors.
- JSON import: Uploads JSON to overwrite current data — perfect for backups or transfers.

## Persistence & Storage
- Uses localStorage: No server or database needed; data stays on your local browser and is reloaded when the browser is opened.
- Separate keys for each weekday: Stored as projectData_Monday, projectData_Tuesday, etc.
- Color preferences stored separately: In a projectColors object in localStorage.

## Lightweight, Local, Offline-Ready
- Fully functional offline after first load.
- No frameworks — only HTML, vanilla JavaScript, and Chart.js.
- Zero dependencies outside of Chart.js CDN.
