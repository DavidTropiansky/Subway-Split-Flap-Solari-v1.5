const fs = require('fs');
const express = require('express');
const app = express();

const jsonFilePath = 'output.json'; // Replace with the path to your JSON file

// Function to read JSON file
function readJsonFile() {
    try {
        return JSON.parse(fs.readFileSync(jsonFilePath, 'utf8'));
    } catch (error) {
        console.error('Error reading the JSON file:', error);
        return []; // Return an empty array in case of an error
    }
}

// Initially read the JSON file
let jsonData = readJsonFile();

// Update jsonData every 30 seconds
setInterval(() => { 
    jsonData = readJsonFile();
}, 55000); // 30000 milliseconds = 30 seconds

app.use('/api/arrivals', (req, res) => {
    let r = { data: [] };

    // Convert the object values to an array and then iterate
    Object.values(jsonData).forEach((entry, index) => {
        if (index <= 45) { // ADJUST THIS IF YOU WANT MORE  OR LESS  RESULTS
            let data = {
                line: entry.route_id, 
                stop: entry.current_stop,      // Using route_id as an example
                terminal: entry.last_stop_name,    // Using last_stop_name as an example
                scheduled: entry.arrival_time,
                remarks: entry.service_status  // Using arrival_time as an example
            };

                   // Let's add an occasional delayed flight.
                data.status =  entry.service_status ;
                if (data.status === 'SERVICE CHANGE' || data.status === 'DELAYS') {
                    data.status = 'B';
                } else {
                    data.status = 'A' ;
                }
                
            


            r.data.push(data);
        }
    });

    res.json(r);
});

// Static files and web server setup remain unchanged
app.use('/', express.static('public'));

const port = process.env.PORT || 8080;
app.listen(port);
console.log('split flap started on port ' + port);