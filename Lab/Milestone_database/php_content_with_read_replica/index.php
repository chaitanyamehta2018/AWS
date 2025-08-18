<?php
include 'dbtest.php';

// Insert handler (always via primary)
if ($_SERVER["REQUEST_METHOD"] == "POST" && isset($_POST["name"], $_POST["message"])) {
    $name = $_POST["name"];
    $message = $_POST["message"];

    $stmt = $pdoWrite->prepare("INSERT INTO guestbook (name, message) VALUES (:name, :message)");
    $stmt->execute([':name' => $name, ':message' => $message]);
}

// Read handler (from replica)
$stmt = $pdoRead->query("SELECT * FROM guestbook ORDER BY id DESC");
$rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>

<!DOCTYPE html>
<html>
<head>
    <title>Guestbook - Primary + Replica</title>
</head>
<body>
    <h2>Guestbook (Primary for Writes, Replica for Reads)</h2>

    <form method="post">
        <input type="text" name="name" placeholder="Your Name" required><br><br>
        <textarea name="message" placeholder="Your Message" required></textarea><br><br>
        <button type="submit">Add Entry</button>
    </form>

    <h3>Entries</h3>
    <?php if ($rows): ?>
        <ul>
        <?php foreach ($rows as $row): ?>
            <li><b><?php echo htmlspecialchars($row['name']); ?>:</b> <?php echo htmlspecialchars($row['message']); ?></li>
        <?php endforeach; ?>
        </ul>
    <?php else: ?>
        <p>No entries yet.</p>
    <?php endif; ?>
</body>
</html>
