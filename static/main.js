window.onload = () => {
  const okBtn = document.getElementById("ok-btn");
  const textArea = document.getElementById("speech-result");

  okBtn.onclick = () => {
    const text = textArea.value.trim();
    if (!text) {
      alert("入力が空です。音声入力または手入力してください。");
      return;
    }

    fetch("/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text })
    }).then((res) => {
      if (res.ok) {
        location.reload();
      } else {
        alert("登録に失敗しました。");
      }
    });
  };

  // 削除ボタンの動作
  document.querySelectorAll(".delete").forEach((btn) => {
    btn.onclick = () => {
      const index = btn.dataset.index;
      fetch("/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index: parseInt(index) })
      }).then((res) => {
        if (res.ok) {
          location.reload();
        } else {
          alert("削除に失敗しました。");
        }
      });
    };
  });
};
