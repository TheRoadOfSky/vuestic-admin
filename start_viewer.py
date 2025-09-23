import os
import http.server
import socketserver
import webbrowser

# 生成 HTML（内嵌 JS）
def generate_html(json_file, html_file):
    html_template = """
    <!DOCTYPE html>
    <html lang="zh">
    <head>
        <meta charset="UTF-8">
        <title>Bundle Log 查看器</title>
        <style>
            table {border-collapse: collapse; width: 100%;}
            th, td {border: 1px solid #ddd; padding: 8px; text-align: left;}
            th {background: #f2f2f2; cursor: pointer;}
            input {width: 300px; margin: 10px;}
            .details {margin-top: 20px;}
        </style>
    </head>
    <body>
        <h1>Asset-Bundle 依赖查看器</h1>
        <input type="text" id="search" placeholder="搜索 Asset/Bundle/GUID..." onkeyup="searchTable()">
        <button onclick="loadOldJson()">加载旧日志对比</button>
        <input type="file" id="oldJson" accept=".json" style="display:none;" onchange="compareJson()">
        <table id="assetTable">
            <thead>
                <tr>
                    <th onclick="sortTable(0)">Asset 路径</th>
                    <th onclick="sortTable(1)">依赖 Bundle 数</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody></tbody>
        </table>
        <div id="bundleDetail" class="details"></div>
        <div id="compareResult" class="details"></div>

        <script>
        let data = {}, oldData = {};

        function normalizeData(raw) {
            let normalized = { assets: {}, bundles: raw.bundles || {} };
            if (raw.assets && Array.isArray(raw.assets)) {
                raw.assets.forEach(asset => {
                    normalized.assets[asset.first] = {};
                    if (asset.second && Array.isArray(asset.second)) {
                        asset.second.forEach(bundle => {
                            normalized.assets[asset.first][bundle.first] = bundle.second || [];
                        });
                    }
                });
            } else if (raw.assets && typeof raw.assets === 'object') {
                normalized.assets = raw.assets; // 兼容旧格式
            }
            return normalized;
        }

        fetch('build_log.json').then(r => r.json()).then(d => { 
            data = normalizeData(d); 
            renderTable(); 
        });

        function renderTable() {
            const tbody = document.querySelector('#assetTable tbody');
            tbody.innerHTML = '';
            Object.keys(data.assets).forEach(asset => {
                const bundles = Object.keys(data.assets[asset]).length;
                const row = `<tr><td>${asset}</td><td>${bundles}</td><td><button onclick="showBundles('${asset.replace(/'/g, "\\'")}')">查看依赖</button></td></tr>`;
                tbody.innerHTML += row;
            });
        }

        function searchTable() {
            const input = document.getElementById('search').value.toLowerCase();
            const rows = document.querySelectorAll('#assetTable tbody tr');
            rows.forEach(row => {
                row.style.display = row.textContent.toLowerCase().includes(input) ? '' : 'none';
            });
        }

        function sortTable(col) {
            const table = document.getElementById('assetTable');
            let rows = Array.from(table.querySelectorAll('tbody tr'));
            let ascending = table.dataset.sortDir !== 'asc';
            table.dataset.sortDir = ascending ? 'asc' : 'desc';

            rows.sort((a, b) => {
                let aText = a.cells[col].textContent;
                let bText = b.cells[col].textContent;
                if (col === 1) { // Bundle 数按数值排序
                    aText = parseInt(aText) || 0;
                    bText = parseInt(bText) || 0;
                }
                return ascending ? (aText > bText ? 1 : -1) : (aText < bText ? 1 : -1);
            });

            const tbody = table.querySelector('tbody');
            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row));
        }

        function showBundles(asset) {
            const bundles = data.assets[asset];
            let html = `<h3>${asset} 依赖:</h3><ul>`;
            Object.keys(bundles).forEach(b => {
                const guids = bundles[b];
                html += `<li>Bundle: ${b} (GUIDs: ${guids.length}) <button onclick="showBundleContent('${b}')">查看内容</button><ul>`;
                guids.forEach(g => html += `<li>GUID: ${g}</li>`);
                html += `</ul></li>`;
            });
            html += `</ul>`;
            document.getElementById('bundleDetail').innerHTML = html;
        }

        function showBundleContent(bundleHash) {
            const bundle = data.bundles[bundleHash];
            if (!bundle) return alert('Bundle 未找到');
            let html = `<h4>Bundle ${bundleHash} (CRC: ${bundle.crc})</h4><ul>`;
            bundle.files.forEach(f => {
                html += `<li>${f.asset_path} (GUID: ${f.guid}, 大小: ${f.size || '未知'})</li>`;
            });
            html += `</ul><p>总文件: ${bundle.files.length}</p>`;
            document.getElementById('bundleDetail').innerHTML += html;
        }

        function loadOldJson() {
            document.getElementById('oldJson').click();
        }

        function compareJson() {
            const file = document.getElementById('oldJson').files[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = e => {
                oldData = normalizeData(JSON.parse(e.target.result));
                performCompare();
            };
            reader.readAsText(file);
        }

        function performCompare() {
            let changes = { addedAssets: [], removedAssets: [], bundleChanges: {} };
            // 对比 Assets
            Object.keys(data.assets).forEach(a => {
                if (!oldData.assets[a]) changes.addedAssets.push(a);
            });
            Object.keys(oldData.assets).forEach(a => {
                if (!data.assets[a]) changes.removedAssets.push(a);
            });
            // 对比 Bundles
            Object.keys(data.bundles).forEach(b => {
                if (!oldData.bundles[b]) {
                    changes.bundleChanges[b] = { status: 'added', files: data.bundles[b].files };
                } else if (JSON.stringify(data.bundles[b].files) !== JSON.stringify(oldData.bundles[b].files)) {
                    changes.bundleChanges[b] = { status: 'modified', files: data.bundles[b].files };
                }
            });
            Object.keys(oldData.bundles).forEach(b => {
                if (!data.bundles[b]) changes.bundleChanges[b] = { status: 'removed' };
            });
            document.getElementById('compareResult').innerHTML = `<h3>变化:</h3><pre>${JSON.stringify(changes, null, 2)}</pre>`;
        }
        </script>
    </body>
    </html>
    """
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_template)

# 主函数
def start_viewer():
    json_file = 'build_log.json'
    html_file = 'viewer.html'

    if not os.path.exists(json_file):
        print(f"错误：{json_file} 不存在，请先运行 convert_log.py 生成 JSON 文件！")
        return

    generate_html(json_file, html_file)

    # 启动本地服务器
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"查看器启动: http://localhost:{PORT}/viewer.html")
        webbrowser.open(f'http://localhost:{PORT}/viewer.html')
        httpd.serve_forever()

if __name__ == '__main__':
    start_viewer()