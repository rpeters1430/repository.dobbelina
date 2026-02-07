import re
from six.moves import urllib_error, urllib_parse, urllib_request

import xbmc


USER_AGENT = (
    "Mozilla/5.0 (compatible, MSIE 11, Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko"
)

MAX_TRIES = 6
COMPONENT = __name__


class NoRedirection(urllib_request.HTTPErrorProcessor):
    def http_response(self, request, response):
        xbmc.log("Stopping Redirect")
        return response

    https_response = http_response


def solve_equation(equation):
    # SECURITY FIX: Disabled unsafe eval() code execution
    # The previous implementation used eval() to execute JavaScript challenge code,
    # which is a security vulnerability even with sanitization attempts.
    #
    # This old Cloudflare bypass method is obsolete. Modern Cloudflare challenges
    # cannot be solved with this approach anyway.
    #
    # Please use FlareSolverr (configured in addon settings) for Cloudflare protection.
    raise NotImplementedError(
        "Old Cloudflare bypass disabled for security reasons. "
        "Please configure FlareSolverr in addon settings."
    )


def solve(url, cj, user_agent=None, wait=True):
    if user_agent is None:
        user_agent = USER_AGENT
    headers = {"User-Agent": user_agent, "Referer": url}
    if cj is not None:
        try:
            cj.load(ignore_discard=True)
        except Exception as e:
            xbmc.log(
                "@@@@Cumination: Error loading cookies in cloudflare.solve: " + str(e),
                xbmc.LOGDEBUG,
            )
        opener = urllib_request.build_opener(urllib_request.HTTPCookieProcessor(cj))
        urllib_request.install_opener(opener)

    request = urllib_request.Request(url)
    for key in headers:
        request.add_header(key, headers[key])
    try:
        response = urllib_request.urlopen(request)
        html = response.read()
    except urllib_error.HTTPError as e:
        html = e.read()

    tries = 0
    while tries < MAX_TRIES:
        solver_pattern = r'var (?:s,t,o,p,b,r,e,a,k,i,n,g|t,r,a),f,\s*([^=]+)={"([^"]+)":([^}]+)};.+challenge-form\'\);.*?\n.*?;(.*?);a\.value'
        vc_pattern = 'input type="hidden" name="jschl_vc" value="([^"]+)'
        pass_pattern = 'input type="hidden" name="pass" value="([^"]+)'
        init_match = re.search(solver_pattern, html, re.DOTALL)
        vc_match = re.search(vc_pattern, html)
        pass_match = re.search(pass_pattern, html)

        if not init_match or not vc_match or not pass_match:
            xbmc.log(
                "Couldn't find attribute: init: |%s| vc: |%s| pass: |%s| No cloudflare check?"
                % (init_match, vc_match, pass_match)
            )
            return False

        init_dict, init_var, init_equation, equations = init_match.groups()
        vc = vc_match.group(1)
        password = pass_match.group(1)

        varname = (init_dict, init_var)
        result = int(solve_equation(init_equation.rstrip()))
        xbmc.log("Initial value: |%s| Result: |%s|" % (init_equation, result))

        for equation in equations.split(";"):
            equation = equation.rstrip()
            if equation[: len(".".join(varname))] != ".".join(varname):
                xbmc.log("Equation does not start with varname |%s|" % (equation))
            else:
                equation = equation[len(".".join(varname)) :]

            expression = equation[2:]
            operator = equation[0]
            if operator not in ["+", "-", "*", "/"]:
                continue

            # SECURITY FIX: Replaced eval() with safe arithmetic operations
            expr_value = solve_equation(expression)
            if operator == "+":
                result = result + expr_value
            elif operator == "-":
                result = result - expr_value
            elif operator == "*":
                result = result * expr_value
            elif operator == "/":
                result = result // expr_value  # Integer division
            result = int(result)

        scheme = urllib_parse.urlparse(url).scheme
        domain = urllib_parse.urlparse(url).hostname
        result += len(domain)

        if wait:
            xbmc.sleep(5000)

        url = "%s://%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s&pass=%s" % (
            scheme,
            domain,
            vc,
            result,
            urllib_parse.quote(password),
        )
        request = urllib_request.Request(url)
        for key in headers:
            request.add_header(key, headers[key])
        try:
            opener = urllib_request.build_opener(NoRedirection)
            urllib_request.install_opener(opener)
            response = urllib_request.urlopen(request)
            while response.getcode() in [301, 302, 303, 307]:
                if cj is not None:
                    cj.extract_cookies(response, request)

                redir_url = response.info().getheader("location")
                if not redir_url.startswith("http"):
                    base_url = "%s://%s" % (scheme, domain)
                    redir_url = urllib_parse.urljoin(base_url, redir_url)

                request = urllib_request.Request(redir_url)
                for key in headers:
                    request.add_header(key, headers[key])
                if cj is not None:
                    cj.add_cookie_header(request)

                response = urllib_request.urlopen(request)
            final = response.read()
            if "cf-browser-verification" in final:
                tries += 1
                html = final
            else:
                break
        except urllib_error.HTTPError:
            return False
        except urllib_error.URLError:
            return False

    if cj is not None:
        cj.save()

    return final
