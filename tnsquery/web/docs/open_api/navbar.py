NAVBAR = """<head>
<style>
:root {
  --nav-element-spacing-vertical: 1rem;
  --nav-element-spacing-horizontal: 0.5rem;
  --nav-link-spacing-vertical: 0.5rem;
  --nav-link-spacing-horizontal: 0.5rem;
  --pico-border-radius: 0.25rem;
}
/**
 * Nav
 */
:where(nav li)::before {
  float: left;
  content: "​";
}

nav,
nav ul {
  display: flex;
}

nav {
  justify-content: space-between;
}
nav ol,
nav ul {
  align-items: center;
  margin-bottom: 0;
  padding: 0;
  list-style: none;
}
nav ol:first-of-type,
nav ul:first-of-type {
  margin-left: calc(var(--nav-element-spacing-horizontal) * -1);
}
nav ol:last-of-type,
nav ul:last-of-type {
  margin-right: calc(var(--nav-element-spacing-horizontal) * -1);
}
nav li {
  display: inline-block;
  margin: 0;
  padding: var(--nav-element-spacing-vertical) var(--nav-element-spacing-horizontal);
}
nav li > * {
  --spacing: 0;
}
nav :where(a, [role=link]) {
  display: inline-block;
  margin: calc(var(--nav-link-spacing-vertical) * -1) calc(var(--nav-link-spacing-horizontal) * -1);
  padding: var(--nav-link-spacing-vertical) var(--nav-link-spacing-horizontal);
  border-radius: var(--pico-border-radius);
  text-decoration: none;
  color: #039be5;
}
nav :where(a, [role=link]):is([aria-current], :hover, :active, :focus) {
  text-decoration: none;
  color: #03a9f4;
}
nav[aria-label=breadcrumb] {
  align-items: center;
  justify-content: start;
}
nav[aria-label=breadcrumb] ul li:not(:first-child) {
  -webkit-margin-start: var(--nav-link-spacing-horizontal);
  margin-inline-start: var(--nav-link-spacing-horizontal);
}
nav[aria-label=breadcrumb] ul li:not(:last-child) ::after {
  position: absolute;
  width: calc(var(--nav-link-spacing-horizontal) * 2);
  -webkit-margin-start: calc(var(--nav-link-spacing-horizontal) / 2);
  margin-inline-start: calc(var(--nav-link-spacing-horizontal) / 2);
  content: "/";
  color: #303446;
  text-align: center;
}
nav[aria-label=breadcrumb] a[aria-current] {
  background-color: transparent;
  color: inherit;
  text-decoration: none;
  pointer-events: none;
}
</style>
<nav>
    <ul>
      <li><strong><a href="/">TNSQUERY</strong></a></li>
    </ul>
    <ul>
      <li><a href="/api/docs#">Docs</a></li>
      <li><a href="/search">Search</a></li>
      <li><a href="https://github.com/emirkmo/tnsquery"">GitHub</a></li>
    </ul>
</nav>
"""


def get_navbar() -> str:
    return NAVBAR
