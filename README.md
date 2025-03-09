# **TallyBox**  
A lightweight simple REST API server for tracking your budget statistics.

## **Endpoints**  

### 🔹 **GET** `/total`  
Retrieves the current total balance.  

**Headers:**  
```
Authorization: Bearer *TALLYBOX_API_GET_TOTAL_TOKEN*
```

**Response:**  
```json
{
  "total": 1999
}
```

---

### 🔹 **GET** `/history`  
Returns the full transaction history.  

**Headers:**  
```
Authorization: Bearer *TALLYBOX_API_GET_HISTORY_TOKEN*
```

**Response:**  
```json5
{
  "history": [
    {
      "amount": -10,
      "comment": "The string (c) copyright",
      "timestamp": 170000000 // Unix timestamp
    }
  ]
}
```

---

### 🔹 **GET** `/data`  
Returns both the current total and transaction history.  

**Headers:**  
```
Authorization: Bearer *TALLYBOX_API_SET_TOKEN*
```

**Response:**  
```json5
{
  "total": 1999,
  "history": [
    // Same structure as in /history
  ]
}
```

---

### 🔹 **POST** `/change`  
Adds a new transaction (income or expense).  

**Headers:**  
```
Authorization: Bearer *TALLYBOX_API_SET_TOKEN*
```

**Request Body:**  
```json5
{
    "amount": -362, // Positive = income, Negative = expense
    "comment": "Dinner with friends"
}
```

**Response:**  
```json5
{
  "success": true,
  "total": 1637, // Updated total balance after processing the request
  "history_record": {
    "amount": -362, // Rounded amount
    "comment": "Dinner with friends", // Trimmed string
    "timestamp": 170000000 // Unix timestamp
  }
}
```

---

## 🚀 **Features**
- 🔹 Simple and lightweight API  
- 🔹 Secure authorization with API tokens  
- 🔹 Supports income & expense tracking  
- 🔹 Provides a full transaction history  

---

# **Setting Up TallyBox**

## **Docker Installation**

To run TallyBox using Docker, follow these steps:

### **1. Set Environment Variables**

Before starting the container, define the required environment variables. You can store them in a `.env` file.

Create a file named `tallybox.env` and add:

```ini
TALLYBOX_API_TOKEN=your_master_token  # Optional, used as default for other tokens if not set
TALLYBOX_API_GET_TOTAL_TOKEN=your_total_token
TALLYBOX_API_GET_HISTORY_TOKEN=your_history_token
TALLYBOX_API_SET_TOKEN=your_set_token
TALLYBOX_DATA_DIR_PATH=/var/lib/tallybox  # Path to store data inside the container
```
(Remove #comments before save please)

Replace `your_master_token`, `your_total_token`, etc., with actual values. (generate random)

### **2. Run the Docker Container**

Use the following command to start the TallyBox container:

```bash
docker run -d \
  --publish 1234:8080 \
  --env-file /path/to/secrets/tallybox.env \
  -v /tallybox-data:/var/lib/tallybox \
  --restart=always \
  --name=tallybox-container \
  fazziclay/tallybox:latest
```

### **Explanation of the Command:**

- `-d` → Runs the container in detached mode.
- `--publish 1234:8080` → Maps port 8080 in the container to port 1234 on the host.
- `--env-file /path/to/secrets/tallybox.env` → Loads environment variables from the `.env` file.
- `-v /tallybox-data:/var/lib/tallybox` → Mounts a local directory to store persistent data.
- `--restart=always` → Ensures the container restarts automatically if it crashes or reboots.
- `--name=tallybox-container` → Assigns a custom name to the container.
- `fazziclay/tallybox:latest` → Uses the latest TallyBox image from Docker Hub.

### **3. Verify the Container is Running**

After starting the container, check its status:

```bash
docker ps | grep tallybox-container
```

If everything is set up correctly, TallyBox should now be running on `http://your-host-ip:1234` or your configured port.

---

Now you’re ready to use TallyBox! 🚀


---

## Data Storage
It's very simple
```bash
/path/to/data/
├── total.txt       # Stores the total balance
├── history.json    # Stores transaction history
├── version.txt     # Stores version information
```

## 📌 **TODO**
- 🔹 Add paginator for history...
