const chocos = document.querySelectorAll(".box");
const currentPath = window.location.pathname;
const path = currentPath.split("/")[2].split(".")[0];

chocos.forEach((choco, index) => {
  const chocoName = choco.querySelector(".detail-box h6").textContent.trim();
  const chocoId = index + 1;
  const chocoPrice = choco
    .querySelector(".detail-box h5")
    .textContent.trim()
    .slice(1);

  const buyButton = choco.querySelector(".buy");
  buyButton.addEventListener("click", async (event) => {
    event.preventDefault();
    await logAction(chocoName, chocoId, chocoPrice, "buy", path);
    return false;
  });
});

async function logAction(
  chocoName,
  chocoId,
  chocoPrice,
  actionName,
  currentPath
) {
  const logData = {
    chocoName,
    chocoId,
    chocoPrice,
    actionName,
    currentPath,
    timestamp: new Date().toISOString(),
  };
  console.log(logData);

  try {
    const response = await fetch("http://localhost:3000/log", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(logData),
    });
  } catch (error) {
    console.error("Error logging action:", error);
    return false;
  }
}
