Getting on the site
1. Start app.py
2. http://127.0.0.1:5000/
---------------------------------
Files that are relevant
1. style.css
   Mostly:
   header.main-header {
    width: 100%;
    background: #4a6cf7;
    color: white;
    padding: 20px 0;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

.header-inner {
    width: 100%;
    max-width: none;
    margin: 0;
    padding: 0 40px; /* optional padding */
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
}

.header-title {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    font-size: 26px;
    font-weight: bold;
}

.header-user {
    margin-left: auto;
    font-size: 14px;
    display: flex;
    gap: 10px;
    padding-right: 10px;
    white-space: nowrap;
}

.header-left {
    flex: 1;
}
2. home.html
