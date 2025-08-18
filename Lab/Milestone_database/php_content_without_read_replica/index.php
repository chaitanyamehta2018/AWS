<?php
 include 'dbtest.php'; 
// Insert data into the database 
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['submit'])) { 
    $name = $_POST['name']; 
    $message = $_POST['message']; 
    $stmt = $pdo->prepare("INSERT INTO guestbook (name, message) VALUES (?, ?)"); 
    $stmt->execute([$name, $message]); 
} 
// Search functionality 
$searchResults = []; 
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST['search'])) { 
    $searchName = $_POST['search_name']; 
    $stmt = $pdo->prepare("SELECT name, message FROM guestbook WHERE name LIKE ?"); 
    $stmt->execute(["%$searchName%"]); 
    $searchResults = $stmt->fetchAll(); 
} 
?> 
<!DOCTYPE html> 
<html lang="en"> 
<head> 
    <meta charset="UTF-8"> 
    <meta name="viewport" content="width=device-width, initial-scale=1.0"> 
    <title>Professional Guestbook</title> 
    <!-- Bootstrap CSS --> 
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css"; 
rel="stylesheet"> 
    <style> 
        body { 
            background-color: #f8f9fa; 
        } 
        .container { 
            margin-top: 50px; 
        } 
        .card { 
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); 
        } 
        footer { 
            margin-top: 40px; 
            text-align: center; 
            background-color: #343a40; 
            color: #fff; 
            padding: 10px; 
        } 
    </style> 
</head> 
<body> 
    <div class="container"> 
        <h1 class="text-center mb-4">Guestbook</h1> 
        <!-- Display Server Hostname --> 
        <p class="text-center text-muted"> 
            You got this page from server with hostname: <strong><?php echo gethostname(); ?></strong> 
        </p> 
        <div class="row"> 
            <div class="col-md-6"> 
                <div class="card p-4"> 
                    <h3 class="mb-3">Add a Message</h3> 
                    <form method="post" action="<?php echo $_SERVER['PHP_SELF']; ?>"> 
                        <div class="mb-3"> 
                            <label for="name" class="form-label">Name</label> 
                            <input type="text" class="form-control" id="name" name="name" placeholder="Enter 
your name" required> 
                        </div> 
                        <div class="mb-3"> 
                            <label for="message" class="form-label">Message</label> 
                            <textarea class="form-control" id="message" name="message" rows="4" 
placeholder="Enter your message" required></textarea> 
                        </div> 
                        <button type="submit" name="submit" class="btn btn-primary w-100">Submit</button> 
                    </form> 
                </div> 
            </div> 
            <div class="col-md-6"> 
                <div class="card p-4"> 
                    <h3 class="mb-3">Search Messages</h3> 
                    <form method="post" action="<?php echo $_SERVER['PHP_SELF']; ?>"> 
                        <div class="mb-3"> 
                            <label for="search_name" class="form-label">Search by Name</label> 
                            <input type="text" class="form-control" id="search_name" name="search_name" 
placeholder="Enter a name"> 
                        </div> 
                        <button type="submit" name="search" class="btn btn-secondary w-100">Search</button> 
                    </form> 
                    <?php if (!empty($searchResults)): ?> 
                        <div class="mt-4"> 
                            <h5>Search Results:</h5> 
                            <?php foreach ($searchResults as $row): ?> 
                                <p><strong><?php echo htmlspecialchars($row['name']); ?></strong>: <?php echo 
htmlspecialchars($row['message']); ?></p> 
                            <?php endforeach; ?> 
                        </div> 
                    <?php endif; ?> 
                </div> 
            </div> 
        </div> 
        <div class="mt-5"> 
            <h3 class="text-center">All Messages</h3> 
            <div class="card p-4"> 
                <?php 
                $stmt = $pdo->query("SELECT name, message FROM guestbook"); 
                while ($row = $stmt->fetch()) { 
                    echo "<p><strong>" . htmlspecialchars($row['name']) . "</strong>: " . 
htmlspecialchars($row['message']) . "</p>"; 
                } 
                ?> 
            </div> 
        </div> 
    </div> 
    <footer> 
        <p>&copy; <?= date('Y'); ?> Powered by CloudFolks Hub</p> 
    </footer> 
    <!-- Bootstrap JS --> 
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js">
 </script>;
 </body> 
</html>