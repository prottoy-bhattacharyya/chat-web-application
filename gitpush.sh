read -p "commit msg: " msg

git add .
echo "added"
git commit -m "$msg"
echo "commited: $msg"
git push origin main
echo "pushed successfully"