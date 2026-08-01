import salmanLogo from "../../Salman_khan_tweet_logo.jpg";
import { Mark } from "./Mark";

export function ProfileIdentity({ hero = false, showMark = false }) {
  return (
    <div className={`identity${hero ? " hero-identity" : ""}`}>
      <div
        className="avatar tweet-avatar"
        role="img"
        aria-label="Salman Khan profile photograph"
        style={{ backgroundImage: `url(${salmanLogo})` }}
      />
      <div>
        <strong>
          Salman Khan <i>✓</i>
        </strong>
        <span>@BeingSalmanKhan</span>
      </div>
      {showMark && <Mark />}
    </div>
  );
}
