// Client-side Mailchimp subscribe via their classic JSONP endpoint — no API
// key, no backend needed. Mailchimp's /subscribe/post endpoint doesn't send
// CORS headers, so a plain fetch() can't read the response; JSONP (a <script>
// tag) sidesteps that entirely.

const MAILCHIMP_ACTION_URL =
  'https://print-iq.us19.list-manage.com/subscribe/post-json?u=c415f819c4a9304cce9148815&id=9ca35fe424&f_id=008bb8e7f0';

// Honeypot field — must always be submitted empty. Real users never see or
// fill it in; bots that auto-fill every field get silently rejected.
const HONEYPOT_FIELD = 'b_c415f819c4a9304cce9148815_9ca35fe424';

interface MailchimpResult {
  success: boolean;
  message: string;
}

function stripHtml(html: string): string {
  const div = document.createElement('div');
  div.innerHTML = html;
  return div.textContent || div.innerText || '';
}

export function subscribeToMailchimp(email: string, firstName: string): Promise<MailchimpResult> {
  return new Promise((resolve) => {
    const callbackName = `mcCallback_${Date.now()}_${Math.floor(Math.random() * 1e6)}`;
    const script = document.createElement('script');

    const cleanup = () => {
      delete (window as any)[callbackName];
      script.remove();
    };

    (window as any)[callbackName] = (data: { result: string; msg: string }) => {
      cleanup();
      resolve({
        success: data.result === 'success',
        message: stripHtml(data.msg || ''),
      });
    };

    script.onerror = () => {
      cleanup();
      resolve({ success: false, message: 'Something went wrong. Please try again.' });
    };

    const params = new URLSearchParams({
      EMAIL: email,
      FNAME: firstName,
      [HONEYPOT_FIELD]: '',
      c: callbackName,
    });

    script.src = `${MAILCHIMP_ACTION_URL}&${params.toString()}`;
    document.body.appendChild(script);
  });
}
