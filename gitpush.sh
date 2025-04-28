read -p "commit msg: " msg

git add .
echo "all files added"
git commit -m "$msg"
echo "all files commited: $msg"
git push origin main
echo "all files pushed successfully"
