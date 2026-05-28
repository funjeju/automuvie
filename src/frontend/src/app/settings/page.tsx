import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";

export default function SettingsPage() {
  return (
    <div className="mx-auto max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle>Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted">
            MVP에서는 Firebase Auth 로그인을 옵션으로 제공합니다. env에 NEXT_PUBLIC_FIREBASE_* 값을 채우면
            구글 로그인이 활성화됩니다. 미설정 시 NEXT_PUBLIC_DEV_UID 기반 dev 토큰으로 동작합니다.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
