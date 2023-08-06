
try {
    new Function("import('/reactfiles/frontend/main.23e8b6a9.js')")();
} catch (err) {
    var el = document.createElement('script');
    el.src = '/reactfiles/frontend/main.23e8b6a9.js';
    el.type = 'module';
    document.body.appendChild(el);
}
